# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

AIM (Advaita Inquiry Matrix) is a Streamlit chat app that acts as an Advaita Vedānta teacher. A deterministic
Python state machine diagnoses the student's misidentification error and picks a teaching method (prakriyā);
Claude API calls turn that directive into natural-language teaching. The README's directory layout is
conceptual and partly stale (it names `teaching_engine/`, `corpus/commentaries/`, `system/dialogue_protocols/`,
none of which exist). The actual runtime is `engine/`, `llm_session.py`, `aim_app.py`, `prompts/`, and
`corpus_database.json`.

## Commands

`pytest` and `pyyaml` are not in `requirements.txt`; install them separately.

```bash
pip install -r requirements.txt pytest
cp .streamlit/secrets_template.toml .streamlit/secrets.toml   # or put ANTHROPIC_API_KEY in .env
streamlit run aim_app.py
```

Tests (no API key needed; the LLM client is mocked). `tests/test_llm_session.py` needs the `anthropic`
package and skips itself otherwise:

```bash
python -m pytest tests/                                            # full suite, needs Scherf_API (see below)
python -m pytest tests/ --ignore=tests/test_scherf_validation.py   # runs anywhere
python -m pytest tests/test_guardrail.py::TestValidateGuardrail::test_missing_ok
```

- Always target `tests/`, never bare `pytest`. The root `test_engine.py` is a print-style integration script,
  not a pytest module; collecting it runs `process()` at import and writes to the real `students/` dir.
- `tests/test_scherf_validation.py` (37 tests) imports the `scherf` package from a sibling checkout at
  `<repo parent>/Scherf_API`. Without it the module fails at collection and aborts the whole run, hence
  the `--ignore`. The Scherf tests in `tests/test_guardrail.py` pass vacuously without it because
  `scherf_library_check` swallows the import error. From a `.claude/worktrees/` checkout the sibling path
  resolves inside `.claude/worktrees/`, so it will not be found even if the repo exists.
- `test_engine.py` is runnable, but redirect its output first or it writes to the real `students/`:

```bash
AIM_STUDENTS_DIR=/tmp/aim_students python test_engine.py
```

Corpus rebuild (regenerates the committed root `corpus_database.json` from `corpus/**/*.md`):

```bash
python corpus_loader.py
```

The per-text `.json` files beside the markdown in `corpus/` come from running individual parsers directly
(each has a `__main__`); they are not read by the runtime and several texts have none.

## Architecture

**Two layers, deliberately separated.**
- `engine/` is deterministic. `engine.state_machine.process(event)` never touches natural language; it
  takes one of three event types (`session_open`, `signal`, `session_close`) and returns a *directive*:
  longitudinal stage, presenting error, prakriyā routing, corpus routing, intervention parameters.
  Spec: `system/state_machine/AIM_state_machine_v3.md`.
- `llm_session.py` wraps the engine with four Claude calls, each driven by a markdown system prompt in
  `prompts/`: `signal_extractor` (utterance to JSON signal), `response_generator` (directive to teacher
  utterance), `session_summarizer` (transcript to JSON summary at close), `response_guardrail` (soft
  post-check). JSON calls go through `_call_with_repair`, which retries once with a repair message on
  parse or schema failure.

**The turn loop exists twice.** `llm_session.run_session` is the stdin/stdout loop; `aim_app.py`
re-implements the same loop against Streamlit session state by importing the private `_`-prefixed
helpers. A change to turn handling must land in both.

**Per-turn pipeline:** student text → `_extract_signal` → `process({"event_type": "signal"})` →
`_fetch_corpus(directive)` → `_generate_response` → `_guardrail_check` (logs only, never blocks).

**Persistence is only at session boundaries.** `_handle_signal` loads the student record but never saves
it. Records in `students/<student_id>.json` are written at `session_close` and, on stage promotion, at
`session_open`. Mid-session state lives in `logs/checkpoints/<session_id>.jsonl`; `recover_session`
replays an orphaned checkpoint to perform a missed close. `logs/sessions/` is the full audit log.

**Stage model.** `purva-adhikari` (Stage 0) students get `redirect` directives aimed at the most deficient
qualification (`prakriya_selector.QUALIFICATION_ROUTING`). Promotion to `adhikari` requires two sessions
plus the gate in `student_record.is_ready_for_adhikari`. Later stages advance one at a time in
`_assess_stage_progression` once two sessions exist and the stage's characteristic errors are all
weakening or absent from the record. A confident adhyāsa
marker at Stage 0 switches the stage for that turn's routing only, without saving.

**Two prakriyā vocabularies.** `PRAKRIYA_MAP[error][stage]["primary"]` (e.g. `drg-drsya-viveka`) is
resolved to a `### ` section of `system/state_machine/AIM_prakriya_modules.md` by diacritic-stripped
heading match (falling back to an `**ID:**` line), and that section is injected into the response prompt.
A new module needs a heading whose ASCII form contains the `primary` name; `tests/test_llm_session.py`
derives every `primary` from `PRAKRIYA_MAP` and checks each resolves to its own heading. `PRAKRIYA_MAP[...]["corpus"]["prakriya"]` (e.g. `drashtr-svarupa`)
must equal, after diacritic stripping, the `prakriya` tag on units in `corpus_database.json`. These are
different namespaces; `_query_corpus` falls back to stage plus level when the corpus tag matches nothing.

**Adding or renaming an error type** touches: `PRAKRIYA_MAP` and `ERROR_LAYERS` in
`engine/prakriya_selector.py`; `_ADHYASA_ERRORS` and `_CHARACTERISTIC_ERRORS` in
`engine/state_machine.py`; the taxonomy tables in `prompts/signal_extractor.md` and
`prompts/session_summarizer.md`; and a module section in `AIM_prakriya_modules.md`.

**Runtime-loaded markdown vs. spec.** Only `prompts/*.md` and `AIM_prakriya_modules.md` are read at
runtime. Everything else under `system/` and `pedagogy/` is design documentation; `archive/` is dead.
`corpus/` markdown is parsed by `parsers/` (dispatch table in `corpus_loader.PARSER_MAP`, keyed by
filename prefix) into `corpus_database.json`, which the runtime queries via `engine.corpus_query`.

**Guardrail.** `engine/guardrail.py` has no `anthropic` import so it is testable standalone. Stage 1 calls
the Scherf library and silently returns `[]` when it is absent. Stage 2 is an LLM check that runs on
`GUARDRAIL_MODEL`, passed through the `model` keyword of `_call_with_repair`.

## Environment variables

Loaded from `.env` by `python-dotenv`, or from `st.secrets` copied into `os.environ` by `aim_app.py`.
The `AIM_*` paths and model names are read at module import, so a test that sets one must
`importlib.reload` the module afterwards, as `tests/test_student_record.py` does. The API key is read
lazily on the first call.

| Variable | Default |
|---|---|
| `ANTHROPIC_API_KEY` | required at first API call |
| `AIM_MODEL` | `claude-opus-4-8` |
| `AIM_GUARDRAIL_MODEL` | `claude-haiku-4-5` |
| `AIM_CORPUS_DB` | `<repo>/corpus_database.json` |
| `AIM_STUDENTS_DIR` | `<repo>/students` |
| `AIM_PROMPT_DIR` | `<repo>/prompts` |
| `AIM_LOGS_DIR`, `AIM_CKPT_DIR` | `<repo>/logs/sessions`, `<repo>/logs/checkpoints` |

Runtime modules anchor paths to the repo root via `__file__`, not CWD. Standalone scripts
(`eval_signal_haiku.py`, `tools/`, `py/`, parser `__main__`s) use CWD-relative paths and must run from
the repo root.

## Conventions

- Error, prakriyā, stage, and qualification identifiers are ASCII with hyphens (`deha-adhyasa`,
  `sravana`, `sraddha`). Diacritics appear only in prose, corpus text, and markdown headings.
  `student_record._migrate` exists because a Cyrillic `а` once leaked into a key; keep IDs pure ASCII.
- Source files carry the Apache 2.0 header for "Dev Bhagavān"; match it on new `.py` files.
- The student ID is the free-text name typed on the login form, used verbatim as the record filename
  `students/<name>.json`.
- `students/`, `logs/sessions/`, `logs/checkpoints/` are gitignored runtime output. A handful of May 2026
  session logs and checkpoints are tracked despite the ignore rule; do not add more.
