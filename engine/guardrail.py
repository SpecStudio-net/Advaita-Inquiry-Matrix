"""
Post-generation soft guardrail — validates teacher responses against the
Scherf library (Stage 1, free) and a Haiku LLM check (Stage 2).

Kept separate from llm_session.py so it can be imported and tested without
the `anthropic` package being present.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path


# ---------- Schema validator (used by _call_with_repair) -------------------

def validate_guardrail(obj: dict) -> list:
    """Return a list of schema errors, empty if valid."""
    errors = []
    if "ok" not in obj:
        errors.append("missing: 'ok'")
    if "violations" not in obj:
        errors.append("missing: 'violations'")
    for v in obj.get("violations", []):
        for f in ("type", "evidence", "severity"):
            if f not in v:
                errors.append(f"violation missing: {f!r}")
    return errors


# ---------- Stage 1: Scherf library structural check (no API call) ----------

def scherf_library_check(response: str, directive: dict) -> list:
    """Check the response text against the Scherf library.

    Gracefully returns [] if the library is unavailable — guardrail failure
    must never block the session.
    """
    try:
        _scherf_root = str(Path(__file__).resolve().parent.parent.parent / "Scherf_API")
        if _scherf_root not in sys.path:
            sys.path.insert(0, _scherf_root)
        from scherf.engine import Claim, Interaction
        ix = Interaction()
        ix.assert_claim(Claim.system_stance(response))
        result = ix.check()
        return [
            {
                "type": "library:" + v.axiom_id,
                "evidence": v.explanation[:150],
                "severity": "medium",
                "source": "scherf-library",
                "reframe": v.reframe,
            }
            for v in result.violations
        ]
    except Exception:
        return []


# ---------- Combined guardrail check ---------------------------------------

def guardrail_check(response: str, directive: dict,
                    call_with_repair_fn, prompt_fn,
                    guardrail_model: str) -> dict:
    """Post-generation soft guardrail.

    Parameters
    ----------
    response          : the teacher response to check
    directive         : the state machine directive that produced it
    call_with_repair_fn : llm_session._call_with_repair (injected to avoid coupling)
    prompt_fn         : llm_session._prompt
    guardrail_model   : model id for Stage 2 (e.g. claude-haiku-4-5)

    Returns a dict with 'ok' and 'violations'. Never raises.
    """
    violations: list[dict] = []

    # Stage 1 — Scherf library (free)
    violations.extend(scherf_library_check(response, directive))

    # Stage 2 — Haiku LLM check
    avoid = (directive.get("prakriya") or {}).get("avoid", [])
    error_type = (directive.get("presenting_error") or {}).get("type") or "none"
    stage = (directive.get("longitudinal_state") or {}).get("stage", "unknown")

    try:
        result = call_with_repair_fn(
            prompt_fn("response_guardrail"),
            [{
                "role": "user",
                "content": (
                    f"Student stage: {stage}\n"
                    f"Error being addressed: {error_type}\n"
                    f"Contraindicated prakriyas: {avoid}\n\n"
                    f"## Response to check\n{response}"
                ),
            }],
            validate_guardrail,
            max_tokens=256,
        )
        violations.extend(result.get("violations", []))
    except Exception as exc:
        logging.warning("Guardrail Stage 2 failed (session continues): %s", exc)

    return {"ok": not violations, "violations": violations}
