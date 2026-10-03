"""OpenAI-compatible chat client with a provider chain (NVIDIA -> Gemini -> none) and usage tracking.

The LLM is ONLY used to propose verbatim text spans from an already-fetched, identity-verified page.
It never sees or produces financial values and never decides identity. Every call consumes request budget.
"""
from __future__ import annotations

import json
import os
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
        self._http = httpx.Client(transport=transport, timeout=timeout)

    @property
    def enabled(self) -> bool:
        return bool(self.providers)

    def complete_json(self, user: str, org: str) -> dict | None:
        """Try providers in order; 429/5xx back off once then fall through. Returns parsed JSON or None."""
        for p in self.providers:
            for attempt in range(2):
                if not self.budget.take(org):
                    return None
                self.usage.requests += 1
                self.usage.by_provider[p.name] = self.usage.by_provider.get(p.name, 0) + 1
                try:
                    r = self._http.post(f"{p.base_url}/chat/completions",
                                        headers={"Authorization": f"Bearer {p.api_key}"},
                                        json={"model": p.model, "temperature": 0, "max_tokens": 700,
                                              "response_format": {"type": "json_object"},
                                              "messages": [{"role": "system", "content": SYSTEM},
                                                           {"role": "user", "content": user}]})
                except httpx.HTTPError:
                    self.usage.failures += 1
                    break
                if r.status_code in (429, 500, 502, 503, 504):
                    self.usage.failures += 1
                    if attempt == 0:
                        try:
                            self.sleeper(min(float(r.headers.get("retry-after", "")), 20.0))
                        except ValueError:
                            self.sleeper(1.0)
                        continue
                    break
                if r.status_code != 200:
                    self.usage.failures += 1
                    break
                try:
                    body = r.json()
                    u = body.get("usage") or {}
                    self.usage.prompt_tokens += int(u.get("prompt_tokens") or 0)
                    self.usage.completion_tokens += int(u.get("completion_tokens") or 0)
                    self.usage.cost_usd += (int(u.get("prompt_tokens") or 0) * p.price_in
                                            + int(u.get("completion_tokens") or 0) * p.price_out) / 1e6
                    return json.loads(body["choices"][0]["message"]["content"])
                except (ValueError, KeyError, IndexError, TypeError):
                    self.usage.failures += 1
                    break
        return None
