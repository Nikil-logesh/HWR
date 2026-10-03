"""OpenAI-compatible chat client with a provider chain (NVIDIA -> Gemini -> none) and usage tracking.

The LLM is ONLY used to propose verbatim text spans from an already-fetched, identity-verified page.
It never sees or produces financial values and never decides identity. Every call consumes request budget.
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
from dataclasses import dataclass, field

import httpx

from ..budget import Budget


@dataclass
class Provider:
    name: str
    base_url: str
    model: str
    api_key: str
    price_in: float = 0.0  # USD per 1M input tokens (declared; 0 for free endpoints)
    price_out: float = 0.0
    json_mode: bool = True  # send response_format=json_object (some hosted models reject it: set False)
    extra_body: dict = field(default_factory=dict)  # provider-specific switches, e.g. disable reasoning
    max_tokens: int = 700


@dataclass
class LlmResult:
    data: dict | None
    strict_json: bool = False  # the reply was valid JSON as-is (no fence/think-tag/prose recovery needed)
    provider: str = ""
    latency_s: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    attempts: int = 0
    error: str | None = None


def parse_json_content(text: str) -> tuple[dict | None, bool]:
    """(object, strict). strict=True only if the whole reply parsed as a JSON object. Otherwise try to recover
    from <think> blocks, ``` fences and surrounding prose; recovery is reported, never silently counted as valid."""
    try:
        obj = json.loads(text)
        return (obj, True) if isinstance(obj, dict) else (None, False)
    except (ValueError, TypeError):
        pass
    t = re.sub(r"<think>.*?</think>", "", text or "", flags=re.DOTALL)
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t.strip())
    i, j = t.find("{"), t.rfind("}")
    if i >= 0 and j > i:
        try:
            obj = json.loads(t[i: j + 1])
            return (obj, False) if isinstance(obj, dict) else (None, False)
        except ValueError:
            return None, False
    return None, False


@dataclass
class Usage:
    requests: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    failures: int = 0
    by_provider: dict[str, int] = field(default_factory=dict)


def providers_from_env(env=os.environ) -> list[Provider]:
    out = []
    for tag, name in (("PRIMARY", "primary"), ("FALLBACK", "fallback")):
        base, model, key = (env.get(f"LLM_{tag}_{k}", "") for k in ("BASE_URL", "MODEL", "API_KEY"))
        if base and model and key:
            out.append(Provider(name, base.rstrip("/"), model, key,
                                float(env.get(f"LLM_{tag}_PRICE_IN", 0) or 0), float(env.get(f"LLM_{tag}_PRICE_OUT", 0) or 0)))
    return out


SYSTEM = ("You extract text fields from a company web page. Reply with JSON only. Every value MUST be copied "
          "verbatim from the page text, and evidence_snippet MUST be a verbatim excerpt of the page that contains "
          "the value. Never paraphrase, never infer, never output numbers about finances. If unsure, omit the field.")


class LlmClient:
    def __init__(self, providers: list[Provider], budget: Budget, *, transport: httpx.BaseTransport | None = None,
                 sleeper=time.sleep, timeout: float = 40.0):
        self.providers, self.budget, self.sleeper = providers, budget, sleeper
        self.usage = Usage()
        self._lock = threading.Lock()
        self._local = threading.local()  # per-thread request counter => correct per-company accounting
        self._http = httpx.Client(transport=transport, timeout=timeout)

    def thread_requests(self) -> int:
        """Requests made by the calling thread so far (use before/after deltas for one company)."""
        return getattr(self._local, "n", 0)

    @property
    def enabled(self) -> bool:
        return bool(self.providers)

    def _fail(self) -> None:
        with self._lock:
            self.usage.failures += 1

    def complete(self, user: str, org: str) -> LlmResult:
        """Try providers in order; 429/5xx back off once then fall through. Never raises."""
        res = LlmResult(None)
        for p in self.providers:
            for attempt in range(2):
                if not self.budget.take(org):
                    res.error = "budget_exhausted"
                    return res
                self._local.n = self.thread_requests() + 1
                with self._lock:
                    self.usage.requests += 1
                    self.usage.by_provider[p.name] = self.usage.by_provider.get(p.name, 0) + 1
                res.attempts += 1
                body = {"model": p.model, "temperature": 0, "max_tokens": p.max_tokens,
                        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
                        **p.extra_body}
                if p.json_mode:
                    body["response_format"] = {"type": "json_object"}
                t0 = time.monotonic()
                try:
                    r = self._http.post(f"{p.base_url}/chat/completions",
                                        headers={"Authorization": f"Bearer {p.api_key}"}, json=body)
                except httpx.HTTPError as exc:
                    self._fail()
                    res.error = type(exc).__name__
                    break
                if r.status_code in (429, 500, 502, 503, 504):
                    self._fail()
                    res.error = f"HTTP {r.status_code}"
                    if attempt == 0:
                        try:
                            self.sleeper(min(float(r.headers.get("retry-after", "")), 20.0))
                        except ValueError:
                            self.sleeper(1.0)
                        continue
                    break
                if r.status_code != 200:
                    self._fail()
                    res.error = f"HTTP {r.status_code}"
                    break
                try:
                    payload = r.json()
                    u = payload.get("usage") or {}
                    pt, ct = int(u.get("prompt_tokens") or 0), int(u.get("completion_tokens") or 0)
                    content = payload["choices"][0]["message"]["content"]
                except (ValueError, KeyError, IndexError, TypeError):
                    self._fail()
                    res.error = "malformed_response"
                    break
                with self._lock:
                    self.usage.prompt_tokens += pt
                    self.usage.completion_tokens += ct
                    self.usage.cost_usd += (pt * p.price_in + ct * p.price_out) / 1e6
                data, strict = parse_json_content(content)
                res.provider, res.latency_s = p.name, time.monotonic() - t0
                res.prompt_tokens, res.completion_tokens = pt, ct
                if data is None:
                    self._fail()
                    res.error = "invalid_json"
                    break  # next provider
                res.data, res.strict_json, res.error = data, strict, None
                return res
        return res

    def complete_json(self, user: str, org: str) -> dict | None:
        return self.complete(user, org).data
