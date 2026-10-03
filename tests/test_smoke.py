import json

import signalpost
from signalpost.config import Settings
from signalpost.log import JsonFormatter, get_logger


def test_kit_importable():
    from norway_company_agent.batch import terminal_envelope  # noqa: F401


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("REQUEST_BUDGET_TOTAL", raising=False)
    assert Settings.from_env().request_budget_total == 2000
    monkeypatch.setenv("MAX_WORKERS", "x")
    assert Settings.from_env().max_workers == 8


def test_log_is_json():
    import logging

    rec = logging.LogRecord("t", logging.INFO, "f", 1, "hello", None, None)
    rec.fields = {"org": "1"}
    out = json.loads(JsonFormatter().format(rec))
    assert out["msg"] == "hello" and out["org"] == "1"
    assert get_logger().name == "signalpost"
    assert signalpost.__version__
