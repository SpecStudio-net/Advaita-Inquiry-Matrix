"""
Engine integration test — simulates a two-session student arc.

Session 1: new Stage 0 student, mumuksutva deficient
Session 2: same student, mumuksutva developing, sraddha deficient
Then: a Stage 1 student with deha-adhyasa at sravana
"""

import json
from engine.state_machine import process

SEP = "-" * 60


def show(label, result):
    print(f"\n{SEP}")
    print(f"{label}")
    print(json.dumps(result, indent=2, ensure_ascii=False))


# ── Stage 0: session 1 ──────────────────────────────────────────

show("SESSION OPEN — new student (Stage 0)", process({
    "event_type": "session_open",
    "student_id": "test_student_01",
    "session_id": "s01",
}))

show("MID-SESSION SIGNAL — Stage 0, no error markers", process({
    "event_type": "signal",
    "student_id": "test_student_01",
    "session_id": "s01",
    "signal": {
        "error_markers": [],
        "recognition_markers": [],
        "resistance": {"present": False},
        "register": {"adhikara_apparent": "sarva", "emotional_tone": "curious"},
        "student_statement_type": "question",
        "student_content_summary": "Student asks what the inquiry is about.",
    },
}))

show("SESSION CLOSE — Stage 0 session 1", process({
    "event_type": "session_close",
    "student_id": "test_student_01",
    "session_id": "s01",
    "session_summary": {
        "errors_presented": [
            {"type": "mumuksutva", "status_at_close": "active"}
        ],
        "prakriyas_applied": [],
        "new_errors_surfaced": [],
        "regression_observed": False,
        "recognition_events": [],
        "notes": "Student engaged but motivation is clearly experiential.",
    },
}))


# ── Stage 0: session 2 ──────────────────────────────────────────

show("SESSION OPEN — session 2 (mumuksutva developing, sraddha absent)", process({
    "event_type": "session_open",
    "student_id": "test_student_01",
    "session_id": "s02",
}))

show("SESSION CLOSE — Stage 0 session 2 (mumuksutva developing)", process({
    "event_type": "session_close",
    "student_id": "test_student_01",
    "session_id": "s02",
    "session_summary": {
        "errors_presented": [
            {"type": "mumuksutva", "status_at_close": "weakening"},
        ],
        "prakriyas_applied": [],
        "new_errors_surfaced": [],
        "regression_observed": False,
        "recognition_events": ["Student paused and said 'I've never thought about what I actually want'"],
        "notes": "Genuine moment of reflection. Mumuksutva beginning to stir.",
    },
}))


# ── Stage 1: separate student with deha-adhyasa ─────────────────

show("SESSION OPEN — Stage 1 student, deha-adhyasa active", process({
    "event_type": "session_open",
    "student_id": "test_student_02",
    "session_id": "s01",
}))

# First, simulate a prior session that established deha-adhyasa in the record
from engine import student_record
rec = student_record.load("test_student_02")
student_record.update_longitudinal_stage(rec, "sravana", "medium", "Student accepted pramāṇa and shows genuine jijñāsā.")
student_record.upsert_active_error(rec, "deha-adhyasa", "gross", status="active")
rec["session_history"].append({"session_id": "s00", "date": "2026-04-01T00:00:00+00:00",
    "errors_presented": ["deha-adhyasa"], "prakriyas_applied": [], "qualification_focus": "",
    "response_quality": "resistant", "recognition_events": [], "state_at_close": "sravana", "summary": ""})
student_record.save("test_student_02", rec)

show("SESSION OPEN — Stage 1 student (record primed with deha-adhyasa)", process({
    "event_type": "session_open",
    "student_id": "test_student_02",
    "session_id": "s01",
}))

show("MID-SESSION SIGNAL — deha-adhyasa high confidence", process({
    "event_type": "signal",
    "student_id": "test_student_02",
    "session_id": "s01",
    "signal": {
        "error_markers": [
            {"type": "deha-adhyasa", "confidence": "high",
             "evidence": "Student said 'when I die, I will cease to exist' with existential fear."}
        ],
        "recognition_markers": [],
        "resistance": {"present": True, "type": "deflection"},
        "register": {"adhikara_apparent": "madhyama", "emotional_tone": "distressed"},
        "student_statement_type": "assertion",
        "student_content_summary": "Student expressing fear of death as annihilation of self.",
    },
}))

show("SESSION CLOSE — Stage 1 student", process({
    "event_type": "session_close",
    "student_id": "test_student_02",
    "session_id": "s01",
    "session_summary": {
        "errors_presented": [
            {"type": "deha-adhyasa", "status_at_close": "active"}
        ],
        "prakriyas_applied": [
            {"name": "drg-drsya-viveka", "target_error": "deha-adhyasa", "apparent_effect": "partial"}
        ],
        "new_errors_surfaced": [],
        "regression_observed": False,
        "recognition_events": [],
        "notes": "Body-identity firmly held. Resistance when pointing introduced.",
    },
}))

print(f"\n{SEP}")
print("Test complete. Check students/ for written records.")
