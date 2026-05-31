"""
Prakriyā selection logic — encodes AIM_state_machine_v3.md Section 8.

PRAKRIYA_MAP: (error_type, stage) → routing dict
QUALIFICATION_ROUTING: qualification → orientation mode + corpus routing
CONTRAINDICATIONS: error_type → list of prakriyās to avoid
ERROR_LAYERS: error_type → layer label for student record
"""

# ---------- Prakriyā Map (Section 8) ----------

PRAKRIYA_MAP = {
    "deha-adhyasa": {
        "adhikari": {
            "primary":    "drg-drsya-viveka",
            "supporting": ["adhyaropa-apavada", "analogy-based-pointing"],
            "avoid":      [],
            "corpus": {
                "prakriya":          "drashtr-svarupa",
                "pedagogical_stage": "sravana",
                "adhikara_level":    "sarva",
                "ontological_scope": "dual-register",
            },
        },
        "sravana": {
            "primary":    "drg-drsya-viveka",
            "supporting": ["adhyaropa-apavada", "analogy-based-pointing"],
            "avoid":      [],
            "corpus": {
                "prakriya":          "drashtr-svarupa",
                "pedagogical_stage": "sravana",
                "adhikara_level":    "sarva",
                "ontological_scope": "dual-register",
            },
        },
        "manana": {
            "primary":    "panca-kosa-viveka",
            "supporting": ["avastha-traya", "neti-neti"],
            "avoid":      [],
            "corpus": {
                "prakriya":          "pancakosa-viveka",
                "pedagogical_stage": "manana",
                "adhikara_level":    "madhyama",
                "ontological_scope": "dual-register",
            },
        },
        "nididhyasana": {
            "primary":    "witness-stabilization",
            "supporting": ["neti-neti", "avastha-traya"],
            "avoid":      [],
            "corpus": {
                "prakriya":          "atman-as-witness-pointing",
                "pedagogical_stage": "nididhyasana",
                "adhikara_level":    "uttama",
                "ontological_scope": "dual-register",
            },
        },
    },

    "prana-adhyasa": {
        "adhikari": {
            "primary":    "drg-drsya-viveka",
            "supporting": ["avastha-traya"],
            "avoid":      [],
            "corpus": {
                "prakriya":          "avastha-traya-analysis",
                "pedagogical_stage": "sravana",
                "adhikara_level":    "sarva",
                "ontological_scope": "dual-register",
            },
        },
        "sravana": {
            "primary":    "drg-drsya-viveka",
            "supporting": ["avastha-traya"],
            "avoid":      [],
            "corpus": {
                "prakriya":          "avastha-traya-analysis",
                "pedagogical_stage": "sravana",
                "adhikara_level":    "sarva",
                "ontological_scope": "dual-register",
            },
        },
        "manana": {
            "primary":    "avastha-traya",
            "supporting": ["drg-drsya-viveka"],
            "avoid":      [],
            "corpus": {
                "prakriya":          "avastha-traya-analysis",
                "pedagogical_stage": "manana",
                "adhikara_level":    "madhyama",
                "ontological_scope": "dual-register",
            },
        },
        "nididhyasana": {
            "primary":    "witness-stabilization",
            "supporting": ["avastha-traya"],
            "avoid":      [],
            "corpus": {
                "prakriya":          "atman-as-witness-pointing",
                "pedagogical_stage": "nididhyasana",
                "adhikara_level":    "uttama",
                "ontological_scope": "dual-register",
            },
        },
    },

    "manas-adhyasa": {
        "adhikari": {
            "primary":    "drg-drsya-viveka",
            "supporting": ["consciousness-self-evidence"],
            "avoid":      [],
            "corpus": {
                "prakriya":          "drashtr-svarupa",
                "pedagogical_stage": "sravana",
                "adhikara_level":    "madhyama",
                "ontological_scope": "dual-register",
            },
        },
        "sravana": {
            "primary":    "drg-drsya-viveka",
            "supporting": ["consciousness-self-evidence", "dream-waking-analogy"],
            "avoid":      [],
            "corpus": {
                "prakriya":          "drashtr-svarupa",
                "pedagogical_stage": "sravana",
                "adhikara_level":    "madhyama",
                "ontological_scope": "dual-register",
            },
        },
        "manana": {
            "primary":    "witness-stabilization",
            "supporting": ["subject-object-analysis", "svaprakasa-pointing"],
            "avoid":      [],
            "corpus": {
                "prakriya":          "atman-as-witness-pointing",
                "pedagogical_stage": "manana",
                "adhikara_level":    "madhyama",
                "ontological_scope": "dual-register",
            },
        },
        "nididhyasana": {
            "primary":    "neti-neti",
            "supporting": ["attention-reversal"],
            "avoid":      [],
            "corpus": {
                "prakriya":          "neti-neti-negation",
                "pedagogical_stage": "nididhyasana",
                "adhikara_level":    "uttama",
                "ontological_scope": "paramarathika",
            },
        },
    },

    "vijnana-adhyasa": {
        "manana": {
            "primary":    "understander-inquiry",
            "supporting": ["svaprakasa-pointing", "seeker-inquiry"],
            "avoid":      ["mahavakya-analysis"],
            "corpus": {
                "prakriya":          "inquiry-opening",
                "pedagogical_stage": "manana",
                "adhikara_level":    "uttama",
                "ontological_scope": "dual-register",
            },
        },
        "nididhyasana": {
            "primary":    "seeker-dissolution",
            "supporting": ["mahavakya-contemplation", "direct-pointing"],
            "avoid":      ["mahavakya-analysis"],
            "corpus": {
                "prakriya":          "atman-as-brahman",
                "pedagogical_stage": "nididhyasana",
                "adhikara_level":    "uttama",
                "ontological_scope": "paramarathika",
            },
        },
    },

    # The ānandamaya-kośa (bliss/causal-body) identification.
    # Added by Task 2 audit (2026-06-01): the fifth sheath was absent from the taxonomy.
    # This is the ROOT case — borders the mūlāvidyā limit per the Scherf library
    # (AV15: causal body is the seed of ignorance persisting in suṣupti).
    # Routing PENDING confirmation from the philosophical authority.
    # Pedagogical note: avoid bliss-as-goal-framing (ānandamaya is a kośa rooted in
    # avidyā, not Brahman — Śaṅkara, ānandamayo'bhyāsāt). Like saksi-adhyasa, avoid
    # witness-stabilization at nididhyāsana: the causal-bliss "I" must dissolve, not
    # be reinforced as an object.
    "ananda-adhyasa": {
        "manana": {
            "primary":    "avastha-traya",
            "supporting": ["panca-kosa-viveka", "karana-sarira-analysis"],
            "avoid":      ["bliss-as-goal-framing"],
            "corpus": {
                "prakriya":          "avastha-traya-analysis",
                "pedagogical_stage": "manana",
                "adhikara_level":    "uttama",
                "ontological_scope": "dual-register",
            },
        },
        "nididhyasana": {
            "primary":    "anandamaya-negation",
            "supporting": ["neti-neti", "witness-brahman-identity"],
            "avoid":      ["bliss-as-goal-framing", "witness-stabilization"],
            "corpus": {
                "prakriya":          "pancakosa-viveka",
                "pedagogical_stage": "nididhyasana",
                "adhikara_level":    "uttama",
                "ontological_scope": "paramarathika",
            },
        },
    },

    "saksi-adhyasa": {
        "nididhyasana": {
            "primary":    "witness-brahman-identity",
            "supporting": ["beyond-known-unknown", "apophatic-pointing"],
            "avoid":      ["witness-stabilization"],
            "corpus": {
                "prakriya":          "atman-as-witness-pointing",
                "pedagogical_stage": "nididhyasana",
                "adhikara_level":    "uttama",
                "ontological_scope": "paramarathika",
            },
        },
    },

    # NOTE: visaya-adhyasa-moksa is OUTSIDE the Scherf library's formal scope.
    # Mokṣa is recognition, not a produced state (design doc §9 ruling 2, §11(4)).
    # The library cannot validate this routing. AIM retains it on its own
    # pedagogical authority as a teaching engine. Task 3 validation will not
    # cover this error type.
    "visaya-adhyasa-moksa": {
        "any": {
            "primary":    "nitya-mukta-pointing",
            "supporting": ["seeker-dissolution", "mahavakya-direct-pointing"],
            "avoid":      ["progressive-path-framing"],
            "corpus": {
                "prakriya":          "mahavakya-prakriya",
                "pedagogical_stage": "nididhyasana",
                "adhikara_level":    "uttama",
                "ontological_scope": "paramarathika",
            },
        },
    },
}


# ---------- Stage 0 Qualification Routing (Section 8) ----------

# Priority order for redirect domain selection (Section 5.1)
QUALIFICATION_PRIORITY = [
    "mumuksutva",
    "sraddha",      # sat_sampat sub-quality, pulled to top per spec
    "viveka",
    "vairagya",
    "sama",         # remaining sat_sampat in order of importance for inquiry
    "titiksa",
    "samadhana",
    "dama",
    "uparama",
]

QUALIFICATION_ROUTING = {
    "mumuksutva": {
        "orientation_mode": "samvega-arousal",
        "corpus": {
            "prakriya":          "mumukshutva-pointing",
            "pedagogical_stage": "sravana",
            "adhikara_level":    "sarva",
            "ontological_scope": "dual-register",
        },
    },
    "sraddha": {
        "orientation_mode": "viveka-arousal",
        "corpus": {
            "prakriya":          "sraddha-awakening",
            "pedagogical_stage": "sravana",
            "adhikara_level":    "sarva",
            "ontological_scope": "dual-register",
        },
    },
    "viveka": {
        "orientation_mode": "viveka-arousal",
        "corpus": {
            "prakriya":          "viveka-definition",
            "pedagogical_stage": "sravana",
            "adhikara_level":    "sarva",
            "ontological_scope": "dual-register",
        },
    },
    "vairagya": {
        "orientation_mode": "karma-yoga-orientation",
        "corpus": {
            "prakriya":          "vairagya-arousal",
            "pedagogical_stage": "sravana",
            "adhikara_level":    "sarva",
            "ontological_scope": "dual-register",
        },
    },
    "sama": {
        "orientation_mode": "karma-yoga-orientation",
        "corpus": {
            "prakriya":          "abhyasa-vairagya",
            "pedagogical_stage": "sravana",
            "adhikara_level":    "sarva",
            "ontological_scope": "dual-register",
        },
    },
    "titiksa": {
        "orientation_mode": "viveka-arousal",
        "corpus": {
            "prakriya":          "sadhana-catustaya",
            "pedagogical_stage": "sravana",
            "adhikara_level":    "sarva",
            "ontological_scope": "dual-register",
        },
    },
    "samadhana": {
        "orientation_mode": "karma-yoga-orientation",
        "corpus": {
            "prakriya":          "sadhana-catustaya",
            "pedagogical_stage": "sravana",
            "adhikara_level":    "sarva",
            "ontological_scope": "dual-register",
        },
    },
    "dama": {
        "orientation_mode": "karma-yoga-orientation",
        "corpus": {
            "prakriya":          "ethical-discipline-instruction",
            "pedagogical_stage": "sravana",
            "adhikara_level":    "sarva",
            "ontological_scope": "dual-register",
        },
    },
    "uparama": {
        "orientation_mode": "karma-yoga-orientation",
        "corpus": {
            "prakriya":          "sadhana-catustaya",
            "pedagogical_stage": "sravana",
            "adhikara_level":    "sarva",
            "ontological_scope": "dual-register",
        },
    },
}


# ---------- Error metadata ----------

ERROR_LAYERS = {
    "deha-adhyasa":         "gross",
    "prana-adhyasa":        "vital",
    "manas-adhyasa":        "mental",
    "vijnana-adhyasa":      "intellectual",
    "ananda-adhyasa":       "causal",    # ānandamaya-kośa, root/mūlāvidyā-bordering
    "saksi-adhyasa":        "subtle",
    "visaya-adhyasa-moksa": "liberation",  # outside Scherf library formal scope
}


# ---------- Intervention parameters (derived from stage + error) ----------

_INTERVENTION_BY_STAGE = {
    "purva-adhikari": {
        "tone": "orientation", "depth": "gross",
        "challenge_level": "gentle", "use_analogy": True, "use_scripture": False,
    },
    "adhikari": {
        "tone": "explanation", "depth": "gross",
        "challenge_level": "gentle", "use_analogy": True, "use_scripture": True,
    },
    "sravana": {
        "tone": "explanation", "depth": "gross",
        "challenge_level": "moderate", "use_analogy": True, "use_scripture": True,
    },
    "manana": {
        "tone": "debate", "depth": "subtle",
        "challenge_level": "moderate", "use_analogy": False, "use_scripture": True,
    },
    "nididhyasana": {
        "tone": "contemplative", "depth": "subtle",
        "challenge_level": "direct", "use_analogy": False, "use_scripture": True,
    },
    "jnana-nistha": {
        "tone": "affirmation", "depth": "subtle",
        "challenge_level": "gentle", "use_analogy": False, "use_scripture": True,
    },
}


def get_intervention(stage: str, resistance_present: bool = False) -> dict:
    base = dict(_INTERVENTION_BY_STAGE.get(stage, _INTERVENTION_BY_STAGE["sravana"]))
    if resistance_present and base["challenge_level"] in ("moderate", "direct"):
        base["challenge_level"] = "gentle"
    return base


# ---------- Selection API ----------

def select(error_type: str, stage: str) -> dict:
    """
    Return prakriyā routing for (error_type, stage).
    Falls back to 'any' for errors without stage-specific routing.
    Falls back to sravana if the exact stage has no entry.
    """
    error_map = PRAKRIYA_MAP.get(error_type, {})

    if stage in error_map:
        return error_map[stage]
    if "any" in error_map:
        return error_map["any"]

    # Graceful fallback: use the closest earlier stage
    stage_order = ["adhikari", "sravana", "manana", "nididhyasana"]
    idx = stage_order.index(stage) if stage in stage_order else 1
    for fallback in reversed(stage_order[:idx]):
        if fallback in error_map:
            return error_map[fallback]

    # Last resort: return sravana entry if exists
    return error_map.get("sravana", {"primary": None, "supporting": [], "avoid": [], "corpus": {}})


def get_redirect_domain(record: dict) -> str:
    """
    Return the highest-priority deficient qualification for Stage 0 redirect.
    Checks sat_sampat sub-qualities after the top-level four.
    Returns 'mumuksutva' as default if all statuses are absent (new student).
    """
    qs = record["qualification_status"]
    sat = qs["sat_sampat"]

    for domain in QUALIFICATION_PRIORITY:
        if domain in qs:
            if qs[domain]["status"] != "present":
                return domain
        elif domain in sat:
            if sat[domain]["status"] != "present":
                return domain

    return "mumuksutva"
