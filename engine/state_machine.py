"""
AIM State Machine — main entry point.

process(event: dict) -> dict

Accepts typed event payloads (session_open | signal | session_close)
and returns structured directive payloads. Never touches natural language.
Spec: system/state_machine/AIM_state_machine_v3.md
"""

from datetime import datetime, timezone

from engine import student_record, corpus_query, prakriya_selector


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------- Public API ----------

def process(event: dict) -> dict:
    event_type = event.get("event_type")
    if event_type == "session_open":
        return _handle_session_open(event)
    elif event_type == "signal":
        return _handle_signal(event)
    elif event_type == "session_close":
        return _handle_session_close(event)
    else:
        raise ValueError(f"Unknown event_type: {event_type!r}")


# ---------- Session open ----------

def _handle_session_open(event: dict) -> dict:
    student_id = event["student_id"]
    record = student_record.load(student_id)
    stage = record["longitudinal_state"]["stage"]

    # Check if Stage 0 student has met transition criteria
    if stage == "purva-adhikari" and student_record.is_ready_for_adhikari(record):
        student_record.update_longitudinal_stage(
            record, "adhikari", "medium",
            "All decisive qualifications developing/present across 2+ sessions."
        )
        student_record.save(student_id, record)
        stage = "adhikari"

    if stage == "purva-adhikari":
        return _redirect_directive(record, event)

    # Stage 1+: probe highest-priority active error
    active = [e for e in record.get("active_errors", []) if e["status"] in ("active", "weakening")]
    if active:
        target = active[0]
        prakriya_info = prakriya_selector.select(target["error_type"], stage)
        units = _query_corpus(prakriya_info)
        return _build_directive(
            record=record,
            presenting_error=_error_payload(target),
            prakriya_info=prakriya_info,
            corpus_units=units,
            directive_type="open_probe",
            probe_target=target["error_type"],
            probe_rationale=f"Active from prior session (observed {target['observation_count']}x). "
                            f"Probe to assess current status.",
        )

    return _build_directive(
        record=record,
        presenting_error=_no_error(),
        prakriya_info=None,
        corpus_units=[],
        directive_type="continue",
    )


# ---------- Mid-session signal ----------

_ADHYASA_ERRORS = frozenset({
    "deha-adhyasa", "prana-adhyasa", "manas-adhyasa",
    "vijnana-adhyasa", "saksi-adhyasa", "visaya-adhyasa-moksa",
})


def _handle_signal(event: dict) -> dict:
    student_id = event["student_id"]
    record = student_record.load(student_id)
    stage = record["longitudinal_state"]["stage"]
    signal = event.get("signal", {})

    if stage == "purva-adhikari":
        # Advance immediately if adhyāsa errors appear at medium+ confidence —
        # these are Stage 1+ errors; the student is past the qualification stage.
        confident_adhyasa = [
            m for m in signal.get("error_markers", [])
            if m.get("type") in _ADHYASA_ERRORS
            and m.get("confidence") in ("medium", "high")
        ]
        if confident_adhyasa:
            student_record.update_longitudinal_stage(
                record, "adhikari", "medium",
                "Adhyāsa errors at medium+ confidence observed — student presenting past Stage 0.",
            )
            student_record.save(student_id, record)
            stage = "adhikari"
        else:
            return _redirect_directive(record, event)

    error_markers = signal.get("error_markers", [])
    recognition_markers = signal.get("recognition_markers", [])
    resistance = signal.get("resistance", {})

    if not error_markers:
        # Recognition or neutral — continue or probe qualification shift
        if recognition_markers:
            return _build_directive(
                record=record,
                presenting_error=_no_error(),
                prakriya_info=None,
                corpus_units=[],
                directive_type="open_probe",
                probe_target="weakening-assessment",
                probe_rationale="Recognition markers observed. Assess whether error is genuinely weakening.",
            )
        return _build_directive(
            record=record,
            presenting_error=_no_error(),
            prakriya_info=None,
            corpus_units=[],
            directive_type="continue",
        )

    primary = _select_primary_error(error_markers, record)
    prakriya_info = prakriya_selector.select(primary["type"], stage)
    units = _query_corpus(prakriya_info)
    resistance_present = resistance.get("present", False)
    intervention = prakriya_selector.get_intervention(stage, resistance_present)

    # Check for regression
    directive_type = "continue"
    if _is_regression(primary["type"], stage, record):
        directive_type = "flag_regression"

    return _build_directive(
        record=record,
        presenting_error={
            "type":         primary["type"],
            "layer":        prakriya_selector.ERROR_LAYERS.get(primary["type"], "unknown"),
            "status":       "active",
            "is_recurring": _is_recurring(primary["type"], record),
        },
        prakriya_info=prakriya_info,
        corpus_units=units,
        directive_type=directive_type,
        intervention_override=intervention,
    )


# ---------- Session close ----------

def _handle_session_close(event: dict) -> dict:
    student_id = event["student_id"]
    record = student_record.load(student_id)
    stage = record["longitudinal_state"]["stage"]
    summary = event.get("session_summary", {})

    if stage == "purva-adhikari":
        _update_qualifications_from_summary(record, summary)
        if student_record.is_ready_for_adhikari(record):
            student_record.update_longitudinal_stage(
                record, "adhikari", "medium",
                "All decisive qualifications developing/present across 2+ sessions."
            )
    else:
        _update_errors_from_summary(record, summary, stage)

    session_entry = {
        "session_id":          event.get("session_id", ""),
        "date":                _now(),
        "errors_presented":    [e["type"] for e in summary.get("errors_presented", [])],
        "prakriyas_applied":   summary.get("prakriyas_applied", []),
        "qualification_focus": _get_qualification_focus(stage, record),
        "response_quality":    _infer_response_quality(summary),
        "recognition_events":  summary.get("recognition_events", []),
        "state_at_close":      record["longitudinal_state"]["stage"],
        "summary":             summary.get("notes", ""),
    }
    student_record.append_session(record, session_entry)
    student_record.save(student_id, record)

    return {
        "status":             "closed",
        "longitudinal_state": record["longitudinal_state"],
        "session_id":         event.get("session_id", ""),
    }


# ---------- Directive builders ----------

def _redirect_directive(record: dict, event: dict) -> dict:
    domain = prakriya_selector.get_redirect_domain(record)
    routing = prakriya_selector.QUALIFICATION_ROUTING.get(domain, {})
    corpus_routing = routing.get("corpus", {})
    units = corpus_query.query(
        prakriya=corpus_routing.get("prakriya"),
        pedagogical_stage=corpus_routing.get("pedagogical_stage"),
        adhikara_level=corpus_routing.get("adhikara_level"),
        ontological_scope=corpus_routing.get("ontological_scope"),
        limit=3,
    )
    return {
        "longitudinal_state": record["longitudinal_state"],
        "presenting_error":   _no_error(),
        "prakriya":           None,
        "corpus_routing":     {**corpus_routing, "preferred_unit_ids": [u["id"] for u in units]},
        "intervention":       prakriya_selector.get_intervention("purva-adhikari"),
        "session_directive": {
            "type":             "redirect",
            "redirect_domain":  domain,
            "probe_target":     None,
            "probe_rationale":  f"Stage 0: {domain} is the primary deficient qualification.",
            "notes":            routing.get("orientation_mode", ""),
        },
    }


def _build_directive(
    record: dict,
    presenting_error: dict,
    prakriya_info: dict,
    corpus_units: list,
    directive_type: str,
    probe_target: str = None,
    probe_rationale: str = "",
    intervention_override: dict = None,
) -> dict:
    stage = record["longitudinal_state"]["stage"]
    intervention = intervention_override or prakriya_selector.get_intervention(stage)
    corpus_routing = {}
    prakriya_payload = None

    if prakriya_info:
        corpus_routing = {
            **prakriya_info.get("corpus", {}),
            "preferred_unit_ids": [u["id"] for u in corpus_units],
        }
        prakriya_payload = {
            "primary":    prakriya_info.get("primary"),
            "supporting": prakriya_info.get("supporting", []),
            "avoid":      prakriya_info.get("avoid", []),
        }

    return {
        "longitudinal_state": record["longitudinal_state"],
        "presenting_error":   presenting_error,
        "prakriya":           prakriya_payload,
        "corpus_routing":     corpus_routing,
        "intervention":       intervention,
        "session_directive": {
            "type":            directive_type,
            "probe_target":    probe_target,
            "probe_rationale": probe_rationale,
            "redirect_domain": None,
            "notes":           "",
        },
    }


# ---------- Summary processing ----------

def _update_qualifications_from_summary(record: dict, summary: dict) -> None:
    """Update qualification_status from session_close summary for Stage 0."""
    qs = record["qualification_status"]
    sat = qs["sat_sampat"]

    _TOP_LEVEL_QUALIFICATIONS = {"viveka", "vairagya", "mumuksutva"}
    for err in summary.get("errors_presented", []):
        status_at_close = err.get("status_at_close", "active")
        if status_at_close in ("weakening", "possibly_resolved"):
            domain = err.get("type", "")
            if domain in _TOP_LEVEL_QUALIFICATIONS:
                if qs[domain]["status"] == "absent":
                    student_record.update_qualification(record, domain, "developing")
            elif domain in sat:
                if sat[domain]["status"] == "absent":
                    student_record.update_sat_sampat(record, domain, "developing")


def _update_errors_from_summary(record: dict, summary: dict, stage: str) -> None:
    """Update active_errors from session_close summary for Stage 1+."""
    for err in summary.get("errors_presented", []):
        error_type = err.get("type", "")
        status_at_close = err.get("status_at_close", "active")
        status_map = {
            "active":             "active",
            "weakening":          "weakening",
            "possibly_resolved":  "weakening",
        }
        record_status = status_map.get(status_at_close, "active")

        prakriyas_used = [
            p.get("name") for p in summary.get("prakriyas_applied", [])
            if p.get("target_error") == error_type
        ]
        layer = prakriya_selector.ERROR_LAYERS.get(error_type, "unknown")
        student_record.upsert_active_error(
            record, error_type, layer,
            prakriyas_applied=prakriyas_used,
            status=record_status,
        )

    # Errors that were weakening and did NOT appear this session move to
    # "possibly_resolved". Full resolution is confirmed at the next session's
    # open probe; if the error re-presents, upsert_active_error will reactivate it.
    presented_types = {e.get("type") for e in summary.get("errors_presented", [])}
    for err in record.get("active_errors", []):
        if err["error_type"] not in presented_types and err["status"] == "weakening":
            err["status"] = "possibly_resolved"

    # Assess longitudinal stage progression
    _assess_stage_progression(record, summary)


_STAGE_ORDER = ["adhikari", "sravana", "manana", "nididhyasana", "jnana-nistha"]

# Errors whose weakening is characteristic of each stage transition.
# A student advances from stage N when the characteristic errors of stage N
# are predominantly weakening across sessions AND at least 2 sessions have passed.
_CHARACTERISTIC_ERRORS = {
    "adhikari":      {"deha-adhyasa", "prana-adhyasa"},
    "sravana":       {"deha-adhyasa", "prana-adhyasa", "manas-adhyasa"},
    "manana":        {"manas-adhyasa", "vijnana-adhyasa", "ananda-adhyasa"},
    "nididhyasana":  {"ananda-adhyasa", "saksi-adhyasa"},
}


def _assess_stage_progression(record: dict, summary: dict) -> None:
    """
    Conservative stage-progression logic.

    Advances when: (a) at least 2 sessions in history, AND (b) all characteristic
    errors for the current stage are weakening or absent in the record. Never
    advances more than one stage per session. Never advances jnana-nistha.

    Regression: flagged in summary but NOT immediately applied — requires persistent
    evidence across multiple sessions (probe at session open will surface it).
    """
    stage = record["longitudinal_state"]["stage"]
    sessions = record.get("session_history", [])
    if len(sessions) < 2:
        return
    if stage not in _STAGE_ORDER:
        return  # purva-adhikari handled separately; jnana-nistha is terminal
    idx = _STAGE_ORDER.index(stage)
    if idx >= len(_STAGE_ORDER) - 1:
        return  # already at terminal stage

    characteristic = _CHARACTERISTIC_ERRORS.get(stage, set())
    if not characteristic:
        return

    active_errors = {e["error_type"]: e for e in record.get("active_errors", [])}

    all_weakening = all(
        error_type not in active_errors
        or active_errors[error_type]["status"] in ("weakening",)
        for error_type in characteristic
    )

    if all_weakening:
        next_stage = _STAGE_ORDER[idx + 1]
        student_record.update_longitudinal_stage(
            record, next_stage, "medium",
            f"Characteristic errors for {stage!r} weakening across sessions. "
            f"Conservative advance to {next_stage!r}.",
        )


# ---------- Helpers ----------

def _query_corpus(prakriya_info: dict) -> list:
    if not prakriya_info:
        return []
    c = prakriya_info.get("corpus", {})
    results = corpus_query.query(
        prakriya=c.get("prakriya"),
        pedagogical_stage=c.get("pedagogical_stage"),
        adhikara_level=c.get("adhikara_level"),
        ontological_scope=c.get("ontological_scope"),
        limit=5,
    )
    if not results:
        # Prakriya value didn't match corpus — fall back to stage + level only
        results = corpus_query.query(
            pedagogical_stage=c.get("pedagogical_stage"),
            adhikara_level=c.get("adhikara_level"),
            ontological_scope=c.get("ontological_scope"),
            limit=5,
        )
    return results


def _select_primary_error(error_markers: list, record: dict) -> dict:
    """Pick highest-confidence error; prefer recurring over new."""
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    active_types = {e["error_type"] for e in record.get("active_errors", [])}

    def score(m):
        conf = confidence_order.get(m.get("confidence", "low"), 2)
        recurring = 0 if m.get("type") in active_types else 1
        return (conf, recurring)

    return min(error_markers, key=score)


def _is_recurring(error_type: str, record: dict) -> bool:
    return any(e["error_type"] == error_type for e in record.get("active_errors", []))


def _is_regression(error_type: str, stage: str, record: dict) -> bool:
    """True if this error belongs to an earlier stage than current."""
    stage_order = ["adhikari", "sravana", "manana", "nididhyasana", "jnana-nistha"]
    gross_errors = {"deha-adhyasa", "prana-adhyasa"}
    if error_type in gross_errors and stage in ("nididhyasana", "jnana-nistha"):
        return True
    return False


def _error_payload(active_error: dict) -> dict:
    return {
        "type":         active_error["error_type"],
        "layer":        active_error.get("layer", "unknown"),
        "status":       active_error.get("status", "active"),
        "is_recurring": active_error.get("observation_count", 0) > 1,
    }


def _no_error() -> dict:
    return {"type": None, "layer": None, "status": "none", "is_recurring": False}


def _get_qualification_focus(stage: str, record: dict) -> str:
    if stage == "purva-adhikari":
        return prakriya_selector.get_redirect_domain(record)
    return ""


def _infer_response_quality(summary: dict) -> str:
    errors = summary.get("errors_presented", [])
    if not errors:
        return "mixed"
    statuses = [e.get("status_at_close", "active") for e in errors]
    if all(s in ("weakening", "possibly_resolved") for s in statuses):
        return "receptive"
    if all(s == "active" for s in statuses):
        return "resistant"
    return "mixed"
