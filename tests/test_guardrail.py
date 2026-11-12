"""
Tests for the post-generation soft guardrail (engine/guardrail.py).

Imports directly from engine.guardrail, which has no anthropic dependency.
The Haiku LLM Stage 2 is mocked; only Stage 1 (Scherf library) and the
schema validator are exercised against real code.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Scherf library path
_SCHERF_ROOT = Path(__file__).resolve().parent.parent.parent / "Scherf_API"
if str(_SCHERF_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCHERF_ROOT))

from engine.guardrail import (
    validate_guardrail,
    scherf_library_check,
    guardrail_check,
)


# ---------- validate_guardrail ---------------------------------------------

class TestValidateGuardrail:

    def test_valid_ok_response(self):
        assert validate_guardrail({"ok": True, "violations": []}) == []

    def test_valid_with_violation(self):
        assert validate_guardrail({
            "ok": False,
            "violations": [{"type": "witness-stabilization", "evidence": "...", "severity": "high"}]
        }) == []

    def test_missing_ok(self):
        errs = validate_guardrail({"violations": []})
        assert any("ok" in e for e in errs)

    def test_missing_violations(self):
        errs = validate_guardrail({"ok": True})
        assert any("violations" in e for e in errs)

    def test_violation_missing_fields(self):
        errs = validate_guardrail({
            "ok": False,
            "violations": [{"type": "foo"}]   # missing evidence and severity
        })
        assert len(errs) >= 2


# ---------- scherf_library_check -------------------------------------------

class TestScherfLibraryCheck:

    def test_clean_teaching_question_no_violations(self):
        """A genuine inquiry question should not trip the library guardrail."""
        result = scherf_library_check(
            "What is it that is aware of this thought right now?", {}
        )
        assert result == []

    def test_returns_list(self):
        result = scherf_library_check("Any response text.", {})
        assert isinstance(result, list)

    def test_graceful_on_none_input(self):
        """Must never raise even on bad input."""
        result = scherf_library_check(None, {})   # type: ignore
        assert isinstance(result, list)

    def test_violation_has_required_keys(self):
        """If a violation is returned, it must have type, evidence, severity."""
        result = scherf_library_check(
            "I will steer and optimize your inquiry process.", {}
        )
        for v in result:
            assert "type" in v
            assert "evidence" in v
            assert "severity" in v


# ---------- guardrail_check contract (Stage 2 mocked) ----------------------

class TestGuardrailCheck:

    def _run(self, response: str, directive: dict = None,
             llm_result: dict = None) -> dict:
        """Run guardrail_check with the Haiku call mocked."""
        if llm_result is None:
            llm_result = {"ok": True, "violations": []}

        def fake_repair(system, messages, validate_fn, max_tokens, model=None):
            return llm_result

        return guardrail_check(
            response,
            directive or {},
            call_with_repair_fn=fake_repair,
            prompt_fn=lambda name: f"<prompt:{name}>",
            guardrail_model="claude-haiku-4-5",
        )

    def test_returns_ok_and_violations_keys(self):
        result = self._run("What are you aware of right now?")
        assert "ok" in result
        assert "violations" in result

    def test_ok_true_when_no_violations(self):
        result = self._run("Can you find the one who is asking?")
        assert result["ok"] is True
        assert result["violations"] == []

    def test_llm_violations_surfaced(self):
        v = {"type": "witness-stabilization", "evidence": "rest as awareness", "severity": "high"}
        result = self._run(
            "Just rest as awareness itself.",
            llm_result={"ok": False, "violations": [v]},
        )
        assert not result["ok"]
        assert any(x["type"] == "witness-stabilization" for x in result["violations"])

    def test_avoid_list_passed_in_user_content(self):
        """The directive's avoid list must appear in the message sent to the LLM."""
        directive = {
            "prakriya": {"avoid": ["witness-stabilization"]},
            "presenting_error": {"type": "saksi-adhyasa"},
        }
        captured = {}
        def capture_repair(system, messages, validate_fn, max_tokens, model=None):
            captured["content"] = messages[0]["content"]
            return {"ok": True, "violations": []}

        guardrail_check(
            "You are the witness.", directive,
            call_with_repair_fn=capture_repair,
            prompt_fn=lambda name: "",
            guardrail_model="claude-haiku-4-5",
        )
        assert "witness-stabilization" in captured.get("content", "")
        assert "saksi-adhyasa" in captured.get("content", "")

    def test_never_raises_on_llm_error(self):
        """If the LLM call throws, guardrail must still return a valid dict."""
        def failing_repair(*args, **kwargs):
            raise RuntimeError("API down")

        result = guardrail_check(
            "Some response.", {},
            call_with_repair_fn=failing_repair,
            prompt_fn=lambda name: "",
            guardrail_model="claude-haiku-4-5",
        )
        assert isinstance(result, dict)
        assert "ok" in result
        assert "violations" in result


# ---------- Stage 2 model routing ------------------------------------------

def test_stage2_receives_guardrail_model():
    """guardrail_check must pass guardrail_model through to the LLM call."""
    captured = {}

    def capture_repair(system, messages, validate_fn, max_tokens, model=None):
        captured["model"] = model
        return {"ok": True, "violations": []}

    guardrail_check(
        "Some response.", {},
        call_with_repair_fn=capture_repair,
        prompt_fn=lambda name: "",
        guardrail_model="claude-haiku-4-5",
    )
    assert captured.get("model") == "claude-haiku-4-5"
