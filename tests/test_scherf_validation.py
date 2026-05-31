"""
Task 3 — Validation of AIM against the Scherf library (General Theory).

This module imports the Scherf library from the sibling Scherf_API repo and uses
it as the formal yardstick to validate AIM's diagnostic logic, prakriyā selection,
and epistemic-level classification.

What is validated here (per design doc §9 boundary and task2-pedagogical-assessment.md):
  ✓ Sheath-adhyāsa diagnostic completeness (all 5 kośas + sākṣi)
  ✓ Ontological scope alignment (dual-register → Vyav/Prat; paramarathika → Param)
  ✓ AV18/A13 constraint — witness-stabilization correctly avoided at subtle layers
  ✓ ananda-adhyasa as root case (borders_limit marker present)
  ✓ saksi-adhyasa as A13/AV18 violation, never as something happening to Y
  ✓ Edge cases: unknown errors, stage mismatches, fallback routing

What is NOT validated here (outside formal scope):
  ✗ Stage/qualification progression (sādhana-catuṣṭaya — no Scherf counterpart)
  ✗ visaya-adhyasa-moksa routing (pedagogical authority only; mokṣa out of scope)
  ✗ LLM layer (signal extraction, response generation)

Run:
  python3.11 -m pytest tests/test_scherf_validation.py -v
"""

import sys
import os
from pathlib import Path

# Add the Scherf library to the path.
# Assumes Scherf_API is a sibling of Advaita-Inquiry-Matrix under ~/Documents.
_SCHERF_ROOT = Path(__file__).resolve().parent.parent.parent / "Scherf_API"
if str(_SCHERF_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCHERF_ROOT))

import pytest

# Scherf library imports
from scherf import SELF, Level, State, conventional
from scherf.axioms.state import Sheath, check_sheath_superimposition, check_av18_witness_no_state
from scherf.axioms.core import check_a13
from scherf.engine import Claim, Interaction, classify
from scherf.levels import level_of

# AIM imports
from engine.prakriya_selector import (
    PRAKRIYA_MAP,
    ERROR_LAYERS,
    select,
    QUALIFICATION_ROUTING,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Mapping from AIM error type to the library Sheath constant.
# saksi-adhyasa and visaya-adhyasa-moksa do not map to a kośa.
_ERROR_TO_SHEATH = {
    "deha-adhyasa":    Sheath.ANNAMAYA,
    "prana-adhyasa":   Sheath.PRANAMAYA,
    "manas-adhyasa":   Sheath.MANOMAYA,
    "vijnana-adhyasa": Sheath.VIJNANAMAYA,
    "ananda-adhyasa":  Sheath.ANANDAMAYA,
}

# Mapping from AIM ontological_scope to Scherf Level.
_SCOPE_TO_LEVEL = {
    "dual-register":   (Level.VYAV, Level.PRAT),  # either of these is valid
    "paramarathika":   (Level.PARAM,),
}


# ---------------------------------------------------------------------------
# 1. Sheath-adhyāsa diagnostic completeness
# ---------------------------------------------------------------------------

class TestSheathDiagnostics:
    """Each AIM kośa error type must produce a library Violation on SELF."""

    @pytest.mark.parametrize("error_type,sheath", _ERROR_TO_SHEATH.items())
    def test_sheath_superimposition_detected(self, error_type, sheath):
        v = check_sheath_superimposition(sheath, SELF)
        assert v is not None, (
            f"{error_type}: check_sheath_superimposition({sheath.name}, SELF) "
            f"returned None — library did not detect the violation"
        )
        assert v.axiom_id, f"{error_type}: Violation has no axiom_id"
        assert v.term, f"{error_type}: Violation has no IAST term"
        assert v.explanation, f"{error_type}: Violation has no explanation"
        assert v.reframe, f"{error_type}: Violation has no reframe"

    def test_all_five_sheaths_covered(self):
        """All five kośas have an AIM error type and a library check."""
        assert len(_ERROR_TO_SHEATH) == 5

    def test_sheath_on_conditioned_substrate_not_flagged(self):
        """M7: sheath superimposed on a conditioned entity is not a Self-error."""
        person = conventional("student")
        for sheath in Sheath:
            v = check_sheath_superimposition(sheath, person)
            assert v is None, (
                f"Sheath.{sheath.name} on a Conditioned substrate should not be "
                f"flagged as a Self-misidentification (M7)"
            )


# ---------------------------------------------------------------------------
# 2. ananda-adhyasa — root case / mūlāvidyā border flag
# ---------------------------------------------------------------------------

class TestAnandaAdhyasa:
    """The ānandamaya-kośa (causal body) is the root case — confirmed by ruling (b)."""

    def test_borders_limit_present(self):
        v = check_sheath_superimposition(Sheath.ANANDAMAYA, SELF)
        assert v is not None
        assert v.borders_limit, (
            "ananda-adhyasa must carry borders_limit (§17.2(3) — mūlāvidyā) "
            "to distinguish it as the root case"
        )

    def test_other_sheaths_do_not_border_limit(self):
        for sheath in [Sheath.ANNAMAYA, Sheath.PRANAMAYA, Sheath.MANOMAYA, Sheath.VIJNANAMAYA]:
            v = check_sheath_superimposition(sheath, SELF)
            assert not v.borders_limit, (
                f"Sheath.{sheath.name} should NOT carry a borders_limit marker — "
                f"only ānandamaya borders §17.2(3)"
            )

    def test_ananda_adhyasa_in_aim_map(self):
        assert "ananda-adhyasa" in PRAKRIYA_MAP
        assert "ananda-adhyasa" in ERROR_LAYERS
        assert ERROR_LAYERS["ananda-adhyasa"] == "causal"

    def test_ananda_manana_uses_avastha_traya(self):
        """The three-states analysis is the correct primary at manana for this error."""
        r = select("ananda-adhyasa", "manana")
        assert r["primary"] == "avastha-traya", (
            "avastha-traya must be primary for ananda-adhyasa at manana: "
            "the causal body is what 'remains' in deep sleep (AV15)"
        )

    def test_ananda_avoids_bliss_as_goal(self):
        for stage in ["manana", "nididhyasana"]:
            r = select("ananda-adhyasa", stage)
            assert "bliss-as-goal-framing" in r["avoid"], (
                f"ananda-adhyasa/{stage} must avoid bliss-as-goal-framing "
                f"(ānandamaya is avidyā-rooted, not Brahman — Śaṅkara)"
            )

    def test_ananda_nididhyasana_avoids_witness_stabilization(self):
        """Like saksi-adhyasa, the causal-bliss 'I' must dissolve, not stabilize."""
        r = select("ananda-adhyasa", "nididhyasana")
        assert "witness-stabilization" in r["avoid"], (
            "ananda-adhyasa at nididhyāsana must avoid witness-stabilization: "
            "the subtle causal 'I' dissolves into Brahman-identity, not a refined object"
        )

    def test_ananda_not_routed_at_beginner_stages(self):
        """The causal-body misidentification is never a beginner-stage error."""
        for stage in ["adhikari", "sravana"]:
            assert stage not in PRAKRIYA_MAP["ananda-adhyasa"], (
                f"ananda-adhyasa should have no routing for {stage!r} — "
                f"it is a manana/nididhyāsana-only error"
            )


# ---------------------------------------------------------------------------
# 3. saksi-adhyasa — A13/AV18 validation
# ---------------------------------------------------------------------------

class TestSaksiAdhyasa:
    """sākṣi-adhyāsa is an A13/AV18 violation — but never something happening to Y."""

    def test_a13_witness_does_not_perceive(self):
        """A13: Y never perceives dualistically — the library enforces this."""
        v = check_a13(SELF, conventional("object"))
        assert v is not None
        assert "A13" in v.axiom_id

    def test_av18_witness_not_in_state(self):
        """AV18: Y is never in any state (turīya)."""
        v = check_av18_witness_no_state(SELF, in_some_state=True)
        assert v is not None
        assert "AV18" in v.axiom_id

    def test_av18_witness_not_in_state_false(self):
        """AV18 is satisfied when Y is not claimed to be in a state."""
        v = check_av18_witness_no_state(SELF, in_some_state=False)
        assert v is None

    def test_saksi_avoids_witness_stabilization(self):
        """Confirmed by library ruling 1: saksi-adhyasa routing avoids stabilization."""
        r = select("saksi-adhyasa", "nididhyasana")
        assert "witness-stabilization" in r["avoid"]
        assert r["primary"] == "witness-brahman-identity"

    def test_saksi_only_at_nididhyasana(self):
        """sākṣi-adhyāsa is the subtlest error — nididhyāsana only."""
        assert list(PRAKRIYA_MAP["saksi-adhyasa"].keys()) == ["nididhyasana"]

    def test_jiva_can_be_in_state(self):
        """AV18 constraint applies only to Y — jīvas are correctly in states."""
        jiva = conventional("student")
        v = check_av18_witness_no_state(jiva, in_some_state=True)
        assert v is None, "A jīva being in a state should not violate AV18"


# ---------------------------------------------------------------------------
# 4. Ontological scope alignment (AV22 / K-series)
# ---------------------------------------------------------------------------

class TestOntologicalScopeAlignment:
    """AIM's ontological_scope values must align with library Level constants."""

    def _collect_scopes(self):
        """Extract all (error_type, stage, scope) triples from PRAKRIYA_MAP."""
        triples = []
        for error_type, stage_map in PRAKRIYA_MAP.items():
            for stage, routing in stage_map.items():
                scope = routing.get("corpus", {}).get("ontological_scope")
                if scope:
                    triples.append((error_type, stage, scope))
        return triples

    def test_all_scopes_are_known_values(self):
        for error_type, stage, scope in self._collect_scopes():
            assert scope in _SCOPE_TO_LEVEL, (
                f"{error_type}/{stage}: unknown ontological_scope {scope!r}. "
                f"Expected one of: {list(_SCOPE_TO_LEVEL)}"
            )

    def test_dual_register_maps_to_vyav_or_prat(self):
        """dual-register content should be classified as Vyav or Prat by the library."""
        level = classify("A conventional description of the student's state.")
        assert level in (Level.VYAV, Level.PRAT), (
            "Conventional (dual-register) claims should not be classified as Param"
        )

    def test_param_level_only_for_absolute(self):
        """Param is the Absolute's level alone — no ordinary output should get it."""
        assert level_of(SELF) is Level.PARAM
        assert level_of(conventional("anything")) is not Level.PARAM

    def test_paramarathika_scope_only_at_subtle_stages(self):
        """Param-scope corpus routing should only appear at manana/nididhyāsana."""
        for error_type, stage_map in PRAKRIYA_MAP.items():
            for stage, routing in stage_map.items():
                scope = routing.get("corpus", {}).get("ontological_scope")
                if scope == "paramarathika":
                    assert stage in ("manana", "nididhyasana", "any"), (
                        f"{error_type}/{stage}: paramarathika scope appearing at "
                        f"beginner stage {stage!r} — only appropriate for manana+"
                    )

    def test_adhikari_sravana_always_dual_register(self):
        """Beginner stages must not use paramarathika scope — AV22 protection."""
        for error_type, stage_map in PRAKRIYA_MAP.items():
            for stage in ("adhikari", "sravana"):
                if stage not in stage_map:
                    continue
                scope = stage_map[stage].get("corpus", {}).get("ontological_scope")
                assert scope != "paramarathika", (
                    f"{error_type}/{stage}: paramarathika scope at {stage!r} violates "
                    f"AV22 — beginner-stage content is conventional, not ultimate"
                )


# ---------------------------------------------------------------------------
# 5. Engine-level claim checking via the Scherf library
# ---------------------------------------------------------------------------

class TestEngineClaims:
    """AIM's claim patterns pass through the Scherf engine and produce correct results."""

    def test_conventional_student_description_passes(self):
        """A claim about a student's conventional state at Vyav should be clean."""
        ix = Interaction()
        ix.assert_claim(
            Claim.about("student")
                .says("student identifies with the gross body")
                .at(Level.VYAV)
        )
        result = ix.check()
        assert result.ok, f"Conventional student description should pass: {result}"

    def test_reducing_student_to_identity_at_param_fails(self):
        """Claiming the student IS their misidentification at Param = adhyāsa."""
        ix = Interaction()
        ix.assert_claim(
            Claim.about("student")
                .says("student IS their body — that is their ultimate nature")
                .at(Level.PARAM)
        )
        result = ix.check()
        assert not result.ok
        axiom_ids = " ".join(v.axiom_id for v in result.violations)
        assert "M6" in axiom_ids or "A13" in axiom_ids

    def test_aim_teacher_stance_does_not_objectify(self):
        """AIM's teaching stance supports inquiry — it doesn't model/steer the student."""
        ix = Interaction()
        ix.assert_claim(Claim.system_stance("support the student's own inquiry"))
        result = ix.check()
        assert result.ok

    def test_transient_corpus_content_classified_at_most_vyav(self):
        """Content that appears in waking but not deep sleep is at most Vyav (AV22)."""
        level = classify(
            "The gross body and world are manifest.",
            present_in={State.JAGRAT},
            absent_in={State.SUSUPTI},
        )
        assert level in (Level.VYAV, Level.PRAT), (
            "State-dependent (transient) content cannot be Param (AV22)"
        )

    def test_paramarathika_content_not_context_dependent(self):
        """Ultimate-level content (Param) should not vary across states (AV23)."""
        # The Absolute never manifests empirically — present_in should be empty
        level = classify(
            "Awareness is self-luminous and unchanging.",
            present_in=set(),
            absent_in=set(),
        )
        # Without transience info, classify returns Vyav (conventional) — correct.
        # Param is never returned by classify() for any output.
        assert level is not Level.PARAM, (
            "classify() should never return Param for a system output (AV23)"
        )


# ---------------------------------------------------------------------------
# 6. Edge cases and failure modes
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Boundary conditions implied by the library's state space."""

    def test_unknown_error_type_does_not_crash(self):
        r = select("completely-unknown-adhyasa", "sravana")
        assert isinstance(r, dict)

    def test_select_with_empty_stage_string(self):
        r = select("deha-adhyasa", "")
        assert isinstance(r, dict)

    def test_no_routing_for_purva_adhikari_in_prakriya_map(self):
        """Stage 0 errors are qualification deficiencies, not adhyāsa errors."""
        for error_type in _ERROR_TO_SHEATH:
            assert "purva-adhikari" not in PRAKRIYA_MAP.get(error_type, {}), (
                f"{error_type} should not have a purva-adhikari routing — "
                f"sheath errors belong to Stage 1+"
            )

    def test_visaya_moksa_marked_outside_scope(self):
        """visaya-adhyasa-moksa is in the map (pedagogical) but outside library scope."""
        assert "visaya-adhyasa-moksa" in PRAKRIYA_MAP
        # The library correctly cannot check moksa — it's not a produced state
        # (design doc §11(4)). We verify AIM has the routing but make no claim
        # that the library validates it.

    def test_witness_is_never_conditioned(self):
        """Y is always Absolute — a jīva is always Conditioned (A1/A4)."""
        from scherf import is_absolute, is_conditioned
        assert is_absolute(SELF) and not is_conditioned(SELF)
        jiva = conventional("student")
        assert is_conditioned(jiva) and not is_absolute(jiva)

    def test_second_subject_cannot_be_created(self):
        """A2/A3: exactly one Subject — AIM must never attempt to construct another."""
        from scherf.errors import AdvaitaError
        from scherf.ontology import Subject
        with pytest.raises(AdvaitaError):
            Subject()

    def test_error_layer_ordering_complete(self):
        """Every entry in PRAKRIYA_MAP has a layer in ERROR_LAYERS."""
        for error_type in PRAKRIYA_MAP:
            assert error_type in ERROR_LAYERS, (
                f"{error_type!r} is in PRAKRIYA_MAP but missing from ERROR_LAYERS"
            )
