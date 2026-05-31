# Task 2 — AIM Audit Report

*Auditing the Advaita Inquiry Matrix (AIM) against the Scherf library (Task 1) as the
formal yardstick. Initial assessment + findings by dimension. 2026-06-01.*

Repo audited: `github.com/SpecStudio-net/Advaita-Inquiry-Matrix` (cloned to /tmp).

---

## 0. Initial assessment — what AIM actually is

AIM is **better than "vibe-coded."** The runtime engine is a clean, well-separated
three-layer system that matches the design principle in its own canonical spec
(`AIM_state_machine_v3.md`, dated 2 May 2026):

```
LLM layer (llm_session.py)      — natural language ↔ structured signals
State machine (engine/)         — diagnosis, prakriyā selection, corpus routing, records
Corpus + student records        — corpus_database.json, students/{id}.json
```

The state machine never touches natural language; the LLM layer never makes
pedagogical decisions. This separation is real and correctly implemented:
`aim_app.py` / `llm_session.py` reach the corpus **only** through
`engine/corpus_query.py` — answering the briefing's question ("does runtime code
reference the corpus directly, or only through the teaching engine?") in the right
way. **This is a genuine strength, not a problem.**

**Mapping to the Scherf library (the bridge in design doc §9):**

| AIM construct | Scherf library correlate | Fidelity |
|---|---|---|
| The six `*-adhyasa` error types | `Superimposed(kośa/X, Y)` — *adhyāsa* (M6/M7) | Strong, with one gap (P1) |
| `saksi-adhyasa` routing *avoids* `witness-stabilization` | Library ruling 1: *sākṣi-adhyāsa* must not stabilize the witness-as-object | **Confirmed agreement** ✓ |
| Longitudinal `stage` (purva-adhikari … jnana-nistha) | Outside Scherf scope (*sādhana* scaffolding, design doc §9 boundary) | Correctly outside formal scope |
| `ontological_scope` (dual-register / paramarathika) | `Level_of` (Vyav+Prat vs. Param) | Aligned |
| Design principle: "diagnose the active *adhyāsa*, not the curriculum stage" | The library's whole premise — error is a property of the jīva's claim, checked against the fixed Self | **Deep alignment** ✓ |

The v3 design principle — *"the primary diagnostic input is the presenting error, not
the student's stage"* — is philosophically aligned with the library's error-centric,
witness-as-fixed-reference model. AIM and the General Theory are pulling in the same
direction.

---

## 1. Architectural integrity

| # | Severity | Finding |
|---|---|---|
| **A1** | Low | `AIM_directory_map.txt` is **stale** — the `engine/` package (the actual runtime!) does not appear in it at all, nor do `llm_session.py`, `parsers/`, `aim_app.py`. The map predates the current architecture. |
| **A2** | **High** | **Two incompatible state models coexist.** `pedagogy/advaita_framework/student_state_model.md` defines a **7-state curriculum progression** (Existential Confusion → … → Stabilized Knowledge). The *implemented* engine uses the **stage + presenting-error** model from `AIM_state_machine_v3.md`, which explicitly **supersedes** the older models and rejects the curriculum framing. The 7-state doc still sits in the **active** `pedagogy/` tree (not `archive/`), so a reader cannot tell which is canonical. |
| **A3** | Medium | `system/dialogue_protocols/` is **empty**, yet PROJECT_OVERVIEW maps "Teaching dialogue → dialogue_protocols" as a core layer. The actual dialogue protocol lives in `pedagogy/advaita_framework/dialogue_protocol.md`. The documented architecture and the real layout diverge. |
| **A4** | Medium | **Two** `corpus_database.json` files exist (repo root and `tools/`). `corpus_query.py` loads the root one via a **relative** path; which is authoritative is undocumented, and they may drift. |
| **A5** | ✓ Positive | Corpus is accessed only through `corpus_query` — separation of concerns holds. |

---

## 2. Pedagogical correctness

| # | Severity | Finding |
|---|---|---|
| **P1** | **High — needs your ruling** | **The *ānandamaya-kośa* misidentification is absent from the *adhyāsa* taxonomy.** AIM's six error types (`ERROR_LAYERS`) cover only **four** sheaths — deha/annamaya, prāṇa/prāṇamaya, manas/manomaya, vijñāna/vijñānamaya — plus `saksi-adhyasa` (labeled "subtle") and `visaya-adhyasa-moksa` ("liberation"). The **fifth sheath, ānandamaya (the bliss/causal-body identification)** — which our Task 1 work singled out as the *root, mūlāvidyā-bordering case* (ruling b) — has **no corresponding error type**. This is exactly the gap the General Theory was built to expose. |
| **P2** | ✓ Positive | `saksi-adhyasa` routing sets `"avoid": ["witness-stabilization"]` and routes to `witness-brahman-identity`. This **confirms** library ruling 1: the correction dissolves the witness-as-object into Brahman-identity rather than reinforcing a subtle objectified witness. AIM and the library agree. |
| **P3** | **Medium — needs your ruling** | `visaya-adhyasa-moksa` has a **live routing** in AIM (`nitya-mukta-pointing`, avoid `progressive-path-framing`). The library rules this **out of scope** (experiential, no structural correlate; design doc §9 ruling 2). These aren't necessarily in conflict — the library models *structure*, AIM is a *pedagogy* engine — but we should decide whether AIM's handling is endorsed, flagged as outside-formal-scope, or reconsidered. |
| **P4** | Medium | The superseded 7-state model (A2) is also *pedagogically* divergent: it is curriculum-centric ("where is the student in the sequence?"), which the v3 spec explicitly rejects in favor of error-centric diagnosis. Confirming it dead removes a contradiction in the stated pedagogy, not just the architecture. |

---

## 3. Implementation errors

| # | Severity | Finding |
|---|---|---|
| **I1** | Medium | `llm_session.py`: `MODEL = "claude-opus-4-7"` — a **retired model ID**. Will fail at runtime against the current API. Should be a current model (e.g. `claude-opus-4-8` or a configurable default). |
| **I2** | **High** | `state_machine._assess_stage_progression()` is a **stub**: it computes `regression` and then `pass`-es. Stage 1+ longitudinal progression is **effectively non-functional** — students never advance (or regress) between sravana/manana/nididhyasana based on session evidence. The Stage 0→1 transition *is* implemented; everything above it is inert. |
| **I3** | Medium | Relative paths: `student_record.STUDENTS_DIR = Path("students")` and `corpus_query` / `corpus_database.json` are CWD-relative. Running `streamlit run aim_app.py` vs. tests from the repo root vs. elsewhere will read/write **different** `students/` and corpus locations — silent state fragmentation. |
| **I4** | Medium | `_update_errors_from_summary` (state_machine.py ~line 315): the "resolve errors not seen in 2 sessions" block sets `err["status"] = "weakening"` when it is *already* "weakening" — a **no-op**. Errors are never automatically resolved; `resolve_error()` in student_record.py is never called by the engine. |
| **I5** | Low–Med | Cyrillic-vs-ASCII hazard: `student_record._migrate` exists to fix a past `sraddhа` (Cyrillic U+0430) bug, and `test_engine.py` **still contains** the Cyrillic spelling in its strings (lines 6, 62). The latent encoding bug is patched at load but not eradicated at source. |
| **I6** | Low | Key-name drift: signal markers use `"type"`; stored errors use `"error_type"`. The engine bridges them correctly today, but the inconsistency is fragile and undocumented. |
| **I7** | Medium | No `requirements.txt` / dependency manifest. Runtime needs `anthropic`, `streamlit`, `python-dotenv`. Not reproducible as-is. |

---

## 4. Test coverage

| # | Severity | Finding |
|---|---|---|
| **T1** | **High** | `test_engine.py` is an **integration script with no assertions** — it prints JSON and has no pass/fail. It cannot catch regressions. |
| **T2** | Medium | It writes to the **real** `students/` directory (`test_student_01/02`), polluting live state and depending on prior-run residue. |
| **T3** | High | **No coverage** of: `corpus_query` (the matching/fallback logic), `prakriya_selector.select` fallback chain, `student_record` qualification transitions, regression detection, or `llm_session` JSON-repair. The one function with the most branching (`select`) is untested. |
| **T4** | Low | `eval_signal_haiku.py` (signal-extraction eval) not yet reviewed — flag for the correction phase. |

---

## 5. Out-of-formal-scope (per design doc §9 boundary)

The following are **structurally outside** what the Scherf library can validate, and
are noted but **not** treated as violations:

- Longitudinal **stage** logic (purva-adhikari … jnana-nistha) and the
  **sādhana-catuṣṭaya** qualification machinery (`QUALIFICATION_ROUTING`,
  `is_ready_for_adhikari`) — pedagogical/temporal scaffolding with no Scherf
  counterpart. (I2 above is a *functional* bug within this scope — the stub — which we
  can still fix as software, even though the library cannot validate its *correctness*.)

---

## 6. Priorities for the correction phase

**Rulings received (2026-06-01):**
- **P1 → Add `ananda-adhyasa`.** Introduce a distinct ānandamaya-kośa (causal-body /
  deep-sleep bliss) error type as the **root case**, with its own prakriyā routing.
  Completes AIM's taxonomy to the full pañca-kośa. Proposed routing in §7 below.
- **P3 → Keep `visaya-adhyasa-moksa`, mark out-of-scope.** AIM retains its pedagogical
  routing (it is a teaching engine, legitimately broader than the formal model), but we
  document that this error type lies outside what the Scherf library can validate. No
  conflict; annotate in code + audit.

**Unblocked.**

**High, unblocked (mechanical/architectural):** I2 (progression stub), T1/T3 (real test
suite), A2 (resolve the dual state model — archive or reconcile).

**Medium:** I1 (model id), I3 (paths), I4 (dead resolution branch), A3/A4 (layout/corpus
clarity), I7 (requirements).

**Low:** A1 (directory map), I5 (Cyrillic eradication), I6 (key naming).

---

---

## 7. Correction spec — `ananda-adhyasa` (P1 ruling)

The ānandamaya-kośa is the **causal body** (*kāraṇa-śarīra*), prominent in deep sleep
(*suṣupti*) and identified by the library (AV15) as the *seed of ignorance*. It is the
**subtlest sheath** — so it is a *manana / nididhyāsana* error, never a beginner error.
Its characteristic presentation is the "I slept happily, I knew nothing" identification,
or mistaking experienced bliss (*ānanda* as object) for the Self.

**`ERROR_LAYERS`:** `"ananda-adhyasa": "causal"` (sits between `intellectual` and
`subtle` in the kośa ordering anna < prāṇa < manas < vijñāna < **ānanda** < [sākṣi]).

**`PRAKRIYA_MAP["ananda-adhyasa"]` (proposed):**

| Stage | primary | supporting | avoid | corpus prakriya / stage / level / scope |
|---|---|---|---|---|
| `manana` | `avastha-traya` | `panca-kosa-viveka`, `karana-sarira-analysis` | `bliss-as-goal-framing` | `avastha-traya-analysis` / manana / uttama / dual-register |
| `nididhyasana` | `anandamaya-negation` | `neti-neti`, `witness-brahman-identity` | `bliss-as-goal-framing`, `witness-stabilization` | `pancakosa-viveka` / nididhyasana / uttama / paramarathika |

**Pedagogical rationale (for the authority's confirmation):**
- *avastha-traya* (three-states analysis) is primary at manana because the causal body
  is precisely what "remains" in deep sleep — the deep-sleep analysis is what exposes
  the ānandamaya identification (AV11/AV15 in the library).
- `avoid: bliss-as-goal-framing` — the characteristic trap here is treating *ānanda*
  (the experienced bliss of the causal sheath) as the goal/Self. Śaṅkara
  (*ānandamayo'bhyāsāt*): ānandamaya is a kośa rooted in *avidyā*, **not** Brahman.
- At nididhyāsana it borders *mūlāvidyā* (design doc §11(3) limit), so the correction
  routes toward `witness-brahman-identity` and, like `saksi-adhyasa`, **avoids
  `witness-stabilization`** — the residual causal-bliss "I" must dissolve, not stabilize.

---

## 8. `visaya-adhyasa-moksa` annotation (P3 ruling)

Retain the existing routing. Add an in-code comment + audit note marking it **outside
the Scherf library's formal scope** (experiential, no structural correlate; design doc
§9 ruling 2, §11(4)). The library will not be used to validate this routing in Task 3.

---

*Next: confirm the §7 routing with the authority, settle repo logistics, then execute
corrections (Sonnet) by priority, expand the test suite, and reassess pedagogical accuracy.*
