"""
Tests for engine/student_record.py.

Covers: create_new structure, load/save, qualification updates, error upsert,
error resolution, stage update, is_ready_for_adhikari, and the Cyrillic migration.
"""

import json
import os
import tempfile
import pytest

# Point AIM_STUDENTS_DIR at a temp directory so tests never touch the real students/ dir.
@pytest.fixture(autouse=True)
def isolated_students_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("AIM_STUDENTS_DIR", str(tmp_path / "students"))
    # Reload to pick up the patched env var
    import importlib
    import engine.student_record as sr
    importlib.reload(sr)
    return tmp_path / "students"


import engine.student_record as sr


def test_create_new_structure():
    rec = sr.create_new("s1")
    assert rec["student_id"] == "s1"
    assert rec["longitudinal_state"]["stage"] == "purva-adhikari"
    assert "viveka" in rec["qualification_status"]
    assert "mumuksutva" in rec["qualification_status"]
    assert "sat_sampat" in rec["qualification_status"]
    assert rec["active_errors"] == []
    assert rec["session_history"] == []

def test_create_new_sat_sampat_keys():
    rec = sr.create_new("s1")
    sat = rec["qualification_status"]["sat_sampat"]
    for key in ("sama", "dama", "uparama", "titiksa", "sraddha", "samadhana"):
        assert key in sat, f"sat_sampat missing {key!r}"
    # Cyrillic variant must NOT be present
    assert "sraddhа" not in sat  # U+0430

def test_load_creates_new_if_absent():
    rec = sr.load("unknown_student")
    assert rec["student_id"] == "unknown_student"

def test_save_and_load_roundtrip():
    rec = sr.create_new("s2")
    sr.update_qualification(rec, "viveka", "present", evidence=["noticed impermanence"])
    sr.save("s2", rec)
    loaded = sr.load("s2")
    assert loaded["qualification_status"]["viveka"]["status"] == "present"

def test_update_qualification():
    rec = sr.create_new("s3")
    sr.update_qualification(rec, "mumuksutva", "developing", evidence=["e1", "e2"])
    q = rec["qualification_status"]["mumuksutva"]
    assert q["status"] == "developing"
    assert "e1" in q["evidence"]

def test_update_sat_sampat():
    rec = sr.create_new("s4")
    sr.update_sat_sampat(rec, "sraddha", "developing")
    assert rec["qualification_status"]["sat_sampat"]["sraddha"]["status"] == "developing"

def test_is_ready_for_adhikari_requires_two_sessions():
    rec = sr.create_new("s5")
    sr.update_qualification(rec, "mumuksutva", "present")
    sr.update_qualification(rec, "viveka", "present")
    sr.update_sat_sampat(rec, "sraddha", "present")
    sr.update_sat_sampat(rec, "sama", "present")
    # No sessions yet
    assert sr.is_ready_for_adhikari(rec) is False

def test_is_ready_for_adhikari_with_sessions():
    rec = sr.create_new("s6")
    sr.update_qualification(rec, "mumuksutva", "present")
    sr.update_qualification(rec, "viveka", "present")
    sr.update_sat_sampat(rec, "sraddha", "present")
    sr.update_sat_sampat(rec, "sama", "present")
    rec["session_history"].append({"session_id": "a"})
    rec["session_history"].append({"session_id": "b"})
    assert sr.is_ready_for_adhikari(rec) is True

def test_is_ready_for_adhikari_missing_qualification():
    rec = sr.create_new("s7")
    sr.update_qualification(rec, "viveka", "present")
    sr.update_sat_sampat(rec, "sraddha", "present")
    sr.update_sat_sampat(rec, "sama", "present")
    rec["session_history"].extend([{"session_id": "a"}, {"session_id": "b"}])
    # mumuksutva still absent
    assert sr.is_ready_for_adhikari(rec) is False

def test_upsert_active_error_creates():
    rec = sr.create_new("s8")
    sr.upsert_active_error(rec, "deha-adhyasa", "gross", status="active")
    assert len(rec["active_errors"]) == 1
    err = rec["active_errors"][0]
    assert err["error_type"] == "deha-adhyasa"
    assert err["observation_count"] == 1
    assert err["status"] == "active"

def test_upsert_active_error_increments():
    rec = sr.create_new("s9")
    sr.upsert_active_error(rec, "deha-adhyasa", "gross")
    sr.upsert_active_error(rec, "deha-adhyasa", "gross")
    assert len(rec["active_errors"]) == 1
    assert rec["active_errors"][0]["observation_count"] == 2

def test_upsert_multiple_errors():
    rec = sr.create_new("s10")
    sr.upsert_active_error(rec, "deha-adhyasa", "gross")
    sr.upsert_active_error(rec, "manas-adhyasa", "mental")
    assert len(rec["active_errors"]) == 2

def test_resolve_error():
    rec = sr.create_new("s11")
    sr.upsert_active_error(rec, "deha-adhyasa", "gross")
    sr.resolve_error(rec, "deha-adhyasa", "sustained probe passed")
    assert all(e["error_type"] != "deha-adhyasa" for e in rec["active_errors"])
    assert any(e["error_type"] == "deha-adhyasa" for e in rec["resolved_errors"])

def test_update_longitudinal_stage():
    rec = sr.create_new("s12")
    sr.update_longitudinal_stage(rec, "sravana", "high", "clear jijñāsā observed")
    assert rec["longitudinal_state"]["stage"] == "sravana"
    assert rec["longitudinal_state"]["confidence"] == "high"

def test_append_session():
    rec = sr.create_new("s13")
    sr.append_session(rec, {"session_id": "x", "date": "2026-01-01T00:00:00+00:00"})
    assert len(rec["session_history"]) == 1
    assert rec["last_session"] == "2026-01-01T00:00:00+00:00"

def test_cyrillic_migration():
    """The Cyrillic-а (U+0430) sraddhа key must be migrated to ASCII sraddha on load."""
    rec = sr.create_new("s14")
    # Manually inject the Cyrillic bug
    sat = rec["qualification_status"]["sat_sampat"]
    sat["sraddhа"] = sat.pop("sraddha")  # inject Cyrillic U+0430
    assert "sraddhа" in sat and "sraddha" not in sat
    migrated = sr._migrate(rec)
    assert "sraddha" in migrated["qualification_status"]["sat_sampat"]
    assert "sraddhа" not in migrated["qualification_status"]["sat_sampat"]
