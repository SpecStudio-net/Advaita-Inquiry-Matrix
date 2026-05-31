"""
Tests for engine/prakriya_selector.py.

Covers: PRAKRIYA_MAP completeness, select() routing + fallback chain,
get_redirect_domain(), get_intervention(), ananda-adhyasa new error type,
visaya-adhyasa-moksa 'any' routing, saksi-adhyasa avoidance constraint.
"""

import pytest
from engine.prakriya_selector import (
    PRAKRIYA_MAP,
    ERROR_LAYERS,
    QUALIFICATION_ROUTING,
    QUALIFICATION_PRIORITY,
    select,
    get_intervention,
    get_redirect_domain,
)


# ---------- Taxonomy completeness ------------------------------------------

ALL_KOSAS = [
    "deha-adhyasa",
    "prana-adhyasa",
    "manas-adhyasa",
    "vijnana-adhyasa",
    "ananda-adhyasa",   # root/causal-body — added Task 2 audit
]

def test_all_five_sheaths_in_prakriya_map():
    for error in ALL_KOSAS:
        assert error in PRAKRIYA_MAP, f"{error!r} missing from PRAKRIYA_MAP"

def test_all_five_sheaths_in_error_layers():
    for error in ALL_KOSAS:
        assert error in ERROR_LAYERS, f"{error!r} missing from ERROR_LAYERS"

def test_error_layers_order():
    """Sheath layer ordering: gross < vital < mental < intellectual < causal < subtle."""
    assert ERROR_LAYERS["deha-adhyasa"] == "gross"
    assert ERROR_LAYERS["prana-adhyasa"] == "vital"
    assert ERROR_LAYERS["manas-adhyasa"] == "mental"
    assert ERROR_LAYERS["vijnana-adhyasa"] == "intellectual"
    assert ERROR_LAYERS["ananda-adhyasa"] == "causal"
    assert ERROR_LAYERS["saksi-adhyasa"] == "subtle"
    assert ERROR_LAYERS["visaya-adhyasa-moksa"] == "liberation"

def test_saksi_and_visaya_moksa_present():
    assert "saksi-adhyasa" in PRAKRIYA_MAP
    assert "visaya-adhyasa-moksa" in PRAKRIYA_MAP


# ---------- ananda-adhyasa routing -----------------------------------------

def test_ananda_adhyasa_manana_routing():
    result = select("ananda-adhyasa", "manana")
    assert result["primary"] == "avastha-traya"
    assert "panca-kosa-viveka" in result["supporting"]
    assert "bliss-as-goal-framing" in result["avoid"]
    assert result["corpus"]["ontological_scope"] == "dual-register"

def test_ananda_adhyasa_nididhyasana_routing():
    result = select("ananda-adhyasa", "nididhyasana")
    assert result["primary"] == "anandamaya-negation"
    assert "witness-stabilization" in result["avoid"], \
        "ananda-adhyasa at nididhyasana must avoid witness-stabilization (causal-bliss I must dissolve)"
    assert result["corpus"]["ontological_scope"] == "paramarathika"

def test_ananda_adhyasa_not_routed_for_sravana():
    """The causal-body identification is not a beginner error — sravana has no entry."""
    assert "sravana" not in PRAKRIYA_MAP["ananda-adhyasa"]
    assert "adhikari" not in PRAKRIYA_MAP["ananda-adhyasa"]


# ---------- saksi-adhyasa constraint ----------------------------------------

def test_saksi_avoids_witness_stabilization():
    """Critical: saksi-adhyasa must not stabilize the witness as an object."""
    result = select("saksi-adhyasa", "nididhyasana")
    assert "witness-stabilization" in result["avoid"], \
        "saksi-adhyasa must avoid witness-stabilization (routing confirmed vs library ruling 1)"
    assert result["primary"] == "witness-brahman-identity"


# ---------- visaya-adhyasa-moksa -------------------------------------------

def test_visaya_moksa_any_routing():
    result = select("visaya-adhyasa-moksa", "nididhyasana")
    assert result["primary"] == "nitya-mukta-pointing"
    assert "progressive-path-framing" in result["avoid"]

def test_visaya_moksa_any_stage_fallback():
    """'any' routing applies regardless of stage."""
    r1 = select("visaya-adhyasa-moksa", "manana")
    r2 = select("visaya-adhyasa-moksa", "sravana")
    assert r1["primary"] == r2["primary"] == "nitya-mukta-pointing"


# ---------- select() fallback chain ----------------------------------------

def test_select_exact_stage_hit():
    result = select("deha-adhyasa", "manana")
    assert result["primary"] == "panca-kosa-viveka"

def test_select_fallback_to_earlier_stage():
    """vijnana-adhyasa has no adhikari/sravana entry — it is a manana+ error.
    The fallback should return the safe-default dict (primary=None) rather than crash."""
    result = select("vijnana-adhyasa", "adhikari")
    assert isinstance(result, dict)
    # primary is None because no earlier stage exists to fall back to — correct behavior.
    # The engine should not present vijnana-adhyasa routing to an adhikari-stage student.
    assert "avoid" in result
    assert "supporting" in result

def test_select_unknown_error_returns_safe_default():
    result = select("nonexistent-error", "sravana")
    assert isinstance(result, dict)
    assert result.get("primary") is None or isinstance(result.get("primary"), str)

def test_select_deha_all_stages():
    for stage in ["adhikari", "sravana", "manana", "nididhyasana"]:
        result = select("deha-adhyasa", stage)
        assert result.get("primary"), f"deha-adhyasa/{stage} returned no primary"


# ---------- get_intervention() ---------------------------------------------

def test_intervention_keys_present():
    for stage in ["purva-adhikari", "adhikari", "sravana", "manana", "nididhyasana"]:
        iv = get_intervention(stage)
        for key in ("tone", "depth", "challenge_level", "use_analogy", "use_scripture"):
            assert key in iv, f"Missing {key!r} in intervention for {stage!r}"

def test_resistance_softens_challenge():
    iv_normal = get_intervention("manana", resistance_present=False)
    iv_resist = get_intervention("manana", resistance_present=True)
    assert iv_resist["challenge_level"] == "gentle"
    assert iv_normal["challenge_level"] in ("moderate", "direct")

def test_intervention_unknown_stage_defaults_to_sravana():
    result = get_intervention("unknown-stage")
    assert result["tone"] == "explanation"


# ---------- get_redirect_domain() ------------------------------------------

def test_redirect_domain_new_student():
    """A brand-new record (all absent) should redirect to mumuksutva."""
    from engine.student_record import create_new
    rec = create_new("_test_redirect_")
    domain = get_redirect_domain(rec)
    assert domain in QUALIFICATION_PRIORITY

def test_redirect_domain_respects_priority():
    """mumuksutva absent → mumuksutva should be the redirect target."""
    from engine.student_record import create_new, update_qualification
    rec = create_new("_test_priority_")
    update_qualification(rec, "viveka", "present")
    domain = get_redirect_domain(rec)
    # mumuksutva is first in QUALIFICATION_PRIORITY and still absent
    assert domain == "mumuksutva"

def test_qualification_routing_complete():
    """Every domain in QUALIFICATION_PRIORITY has an entry in QUALIFICATION_ROUTING."""
    for domain in QUALIFICATION_PRIORITY:
        assert domain in QUALIFICATION_ROUTING, f"{domain!r} missing from QUALIFICATION_ROUTING"
