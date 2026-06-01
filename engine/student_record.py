import json
import os
from datetime import datetime, timezone
from pathlib import Path

try:
    from filelock import FileLock as _FileLock
    _HAS_FILELOCK = True
except ImportError:
    _HAS_FILELOCK = False

# Anchor paths to the repo root (parent of engine/), not the process CWD.
# This prevents students/ and corpus_database.json being created in different
# locations depending on how the app is launched (streamlit vs python -m vs tests).
_REPO_ROOT = Path(__file__).resolve().parent.parent
STUDENTS_DIR = Path(os.environ.get("AIM_STUDENTS_DIR", str(_REPO_ROOT / "students")))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_qualification() -> dict:
    return {"status": "absent", "last_assessed": None, "evidence": [], "corpus_applied": []}


def _new_sat_sampat_quality() -> dict:
    return {"status": "absent", "evidence": []}


def create_new(student_id: str) -> dict:
    now = _now()
    return {
        "student_id": student_id,
        "created": now,
        "last_session": None,
        "longitudinal_state": {
            "stage": "purva-adhikari",
            "confidence": "low",
            "last_updated": now,
            "basis": "New student — no prior sessions.",
        },
        "qualification_status": {
            "viveka":   _new_qualification(),
            "vairagya": _new_qualification(),
            "sat_sampat": {
                "sama":      _new_sat_sampat_quality(),
                "dama":      _new_sat_sampat_quality(),
                "uparama":   _new_sat_sampat_quality(),
                "titiksa":   _new_sat_sampat_quality(),
                "sraddha":   _new_sat_sampat_quality(),
                "samadhana": _new_sat_sampat_quality(),
            },
            "mumuksutva": _new_qualification(),
        },
        "active_errors": [],
        "resolved_errors": [],
        "session_history": [],
        "notes": "",
    }


def _migrate(record: dict) -> dict:
    """Fix records written before the Cyrillic-а → ASCII-a rename."""
    sat = record.get("qualification_status", {}).get("sat_sampat", {})
    if "sraddhа" in sat:  # Cyrillic U+0430
        sat["sraddha"] = sat.pop("sraddhа")
    return record


def load(student_id: str) -> dict:
    STUDENTS_DIR.mkdir(exist_ok=True)
    path = STUDENTS_DIR / f"{student_id}.json"
    if path.exists():
        return _migrate(json.loads(path.read_text(encoding="utf-8")))
    return create_new(student_id)


def save(student_id: str, record: dict) -> None:
    STUDENTS_DIR.mkdir(exist_ok=True)
    path = STUDENTS_DIR / f"{student_id}.json"
    data = json.dumps(record, indent=2, ensure_ascii=False)
    if _HAS_FILELOCK:
        with _FileLock(str(path) + ".lock", timeout=5):
            path.write_text(data, encoding="utf-8")
    else:
        path.write_text(data, encoding="utf-8")


# ---------- Qualification helpers ----------

def update_qualification(
    record: dict,
    qualification: str,
    status: str,
    evidence: list = None,
    corpus_applied: list = None,
) -> None:
    """Update a top-level qualification (viveka, vairagya, mumuksutva)."""
    q = record["qualification_status"][qualification]
    q["status"] = status
    q["last_assessed"] = _now()
    if evidence:
        q["evidence"].extend(evidence)
    if corpus_applied:
        q.setdefault("corpus_applied", []).extend(corpus_applied)


def update_sat_sampat(
    record: dict, quality: str, status: str, evidence: list = None
) -> None:
    """Update a specific ṣaṭ-sampat quality."""
    q = record["qualification_status"]["sat_sampat"][quality]
    q["status"] = status
    if evidence:
        q["evidence"].extend(evidence)


def is_ready_for_adhikari(record: dict) -> bool:
    """
    True when all decisive qualifications are present/developing AND at least
    two prior sessions exist. Per Section 5.1: mumukṣutva + śraddhā + viveka
    + sufficient śama must all be developing or present.
    """
    if len(record.get("session_history", [])) < 2:
        return False
    qs = record["qualification_status"]
    decisive = [
        qs["mumuksutva"]["status"] in ("developing", "present"),
        qs["viveka"]["status"] in ("developing", "present"),
        qs["sat_sampat"]["sraddha"]["status"] in ("developing", "present"),
        qs["sat_sampat"]["sama"]["status"] in ("developing", "present"),
    ]
    return all(decisive)


# ---------- Error helpers ----------

def upsert_active_error(
    record: dict,
    error_type: str,
    layer: str,
    prakriyas_applied: list = None,
    status: str = "active",
    weakening_evidence: list = None,
) -> None:
    now = _now()
    for err in record["active_errors"]:
        if err["error_type"] == error_type:
            err["last_observed"] = now
            err["observation_count"] += 1
            err["status"] = status
            for p in (prakriyas_applied or []):
                if p not in err["prakriyas_applied"]:
                    err["prakriyas_applied"].append(p)
            err["weakening_evidence"].extend(weakening_evidence or [])
            return
    record["active_errors"].append({
        "error_type": error_type,
        "layer": layer,
        "first_observed": now,
        "last_observed": now,
        "observation_count": 1,
        "status": status,
        "weakening_evidence": weakening_evidence or [],
        "prakriyas_applied": prakriyas_applied or [],
    })


def resolve_error(record: dict, error_type: str, resolution_basis: str) -> None:
    record["active_errors"] = [
        e for e in record["active_errors"] if e["error_type"] != error_type
    ]
    record["resolved_errors"].append({
        "error_type": error_type,
        "resolved": _now(),
        "resolution_basis": resolution_basis,
    })


# ---------- Stage helpers ----------

def update_longitudinal_stage(
    record: dict, stage: str, confidence: str, basis: str
) -> None:
    record["longitudinal_state"] = {
        "stage": stage,
        "confidence": confidence,
        "last_updated": _now(),
        "basis": basis,
    }


def append_session(record: dict, session_entry: dict) -> None:
    record["session_history"].append(session_entry)
    record["last_session"] = session_entry.get("date", _now())
