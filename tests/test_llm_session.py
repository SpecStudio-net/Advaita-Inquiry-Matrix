"""
Tests for llm_session.py helpers that need no network: model plumbing in
_call_claude / _call_with_repair, and prakriyā module text lookup.

Requires the `anthropic` package to import llm_session; skipped otherwise.
"""

import pytest

pytest.importorskip("anthropic")

import llm_session as ls
from engine.prakriya_selector import PRAKRIYA_MAP

# A value no .env could plausibly set, so the tests fail against the old
# behaviour even when AIM_MODEL happens to equal AIM_GUARDRAIL_MODEL.
SENTINEL_MODEL = "guardrail-sentinel"


# ---------- Model plumbing -------------------------------------------------

class _FakeMessages:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)

        class _Resp:
            content = [type("Block", (), {"text": '{"ok": true, "violations": []}'})()]
        return _Resp()


class _FakeClient:
    def __init__(self):
        self.messages = _FakeMessages()


@pytest.fixture
def fake_client(monkeypatch):
    client = _FakeClient()
    monkeypatch.setattr(ls, "_get_client", lambda: client)
    return client


def test_call_claude_uses_default_model(fake_client):
    ls._call_claude("sys", [{"role": "user", "content": "hi"}])
    assert fake_client.messages.calls[0]["model"] == ls.MODEL


def test_call_claude_honours_model_override(fake_client):
    ls._call_claude("sys", [{"role": "user", "content": "hi"}], model=SENTINEL_MODEL)
    assert fake_client.messages.calls[0]["model"] == SENTINEL_MODEL


def test_call_with_repair_forwards_model(fake_client):
    ls._call_with_repair(
        "sys", [{"role": "user", "content": "hi"}],
        lambda obj: [], max_tokens=64, model=SENTINEL_MODEL,
    )
    assert fake_client.messages.calls[0]["model"] == SENTINEL_MODEL


def test_guardrail_check_runs_stage2_on_guardrail_model(fake_client, monkeypatch):
    monkeypatch.setattr(ls, "GUARDRAIL_MODEL", SENTINEL_MODEL)
    ls._guardrail_check("Some teacher response.", {})
    models = [c["model"] for c in fake_client.messages.calls]
    assert models == [SENTINEL_MODEL]


# ---------- Prakriyā module lookup -----------------------------------------

def _first_line(text: str) -> str:
    return text.splitlines()[0] if text else ""


PRIMARIES = sorted({
    routing["primary"]
    for stages in PRAKRIYA_MAP.values()
    for routing in stages.values()
    if routing.get("primary")
})


@pytest.mark.parametrize("name", PRIMARIES)
def test_every_primary_resolves_to_its_own_heading(name):
    text = ls._prakriya_module_text(name)
    first = _first_line(text)
    assert first.startswith("### "), f"{name!r} resolved to: {first!r}"
    assert name in ls._normalize_name(first), f"{name!r} resolved to: {first!r}"


@pytest.mark.parametrize("name, heading", [
    ("panca-kosa-viveka",  "### B.3"),   # old lookup hit a cross-reference inside B.1
    ("avastha-traya",      "### B.2"),
    ("neti-neti",          "### B.4"),
])
def test_module_text_starts_at_own_heading(name, heading):
    assert _first_line(ls._prakriya_module_text(name)).startswith(heading)


def test_module_text_is_single_section():
    text = ls._prakriya_module_text("panca-kosa-viveka")
    headings = [l for l in text.splitlines() if l.startswith("### ")]
    assert len(headings) == 1


def test_module_text_unknown_name_is_empty():
    assert ls._prakriya_module_text("no-such-prakriya") == ""


def test_module_text_empty_name_is_empty():
    assert ls._prakriya_module_text("") == ""
