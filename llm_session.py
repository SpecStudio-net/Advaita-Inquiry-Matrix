# Copyright 2026 Dev Bhagavān
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
AIM LLM session layer.

run_session(student_id, session_id)   — interactive session loop
recover_session(student_id, session_id) — replay from orphaned checkpoint
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic
from dotenv import load_dotenv
load_dotenv(override=True)

from engine import corpus_query
from engine.state_machine import process as sm_process

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

# ---------- Config ----------

MODEL = os.environ.get("AIM_MODEL", "claude-opus-4-7")
MAX_API_RETRIES = 3
BACKOFF_BASE = 1.0

PROMPT_DIR = Path("prompts")
PRAKRIYA_MODULES_PATH = Path("system/state_machine/AIM_prakriya_modules.md")
LOGS_DIR = Path("logs/sessions")
CKPT_DIR = Path("logs/checkpoints")


# ---------- Prompt loading (loaded once, cached) ----------

_PROMPTS: dict = {}
_PRAKRIYA_MODULES: str = None


def _prompt(name: str) -> str:
    if name not in _PROMPTS:
        _PROMPTS[name] = (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")
    return _PROMPTS[name]


def _prakriya_module_text(prakriya_name: str) -> str:
    """Extract the section for prakriya_name from AIM_prakriya_modules.md."""
    global _PRAKRIYA_MODULES
    if _PRAKRIYA_MODULES is None:
        _PRAKRIYA_MODULES = (
            PRAKRIYA_MODULES_PATH.read_text(encoding="utf-8")
            if PRAKRIYA_MODULES_PATH.exists() else ""
        )
    if not prakriya_name or not _PRAKRIYA_MODULES:
        return ""

    needle = prakriya_name.lower().replace("-", " ")
    lines = _PRAKRIYA_MODULES.splitlines()
    start = None
    for i, line in enumerate(lines):
        if needle in line.lower() or prakriya_name.lower() in line.lower():
            start = i
            break
    if start is None:
        return ""

    section = []
    for i, line in enumerate(lines[start:], start):
        if i > start and line.startswith("## "):
            break
        section.append(line)
    return "\n".join(section)


# ---------- API wrapper ----------

_client: anthropic.Anthropic = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def _call_claude(system: str, messages: list, max_tokens: int = 1024) -> str:
    """Call Claude with exponential-backoff retry on transient errors."""
    client = _get_client()
    last_exc = None
    for attempt in range(MAX_API_RETRIES):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
            )
            return resp.content[0].text
        except (
            anthropic.APIConnectionError,
            anthropic.RateLimitError,
            anthropic.InternalServerError,
        ) as exc:
            last_exc = exc
            wait = BACKOFF_BASE * (2 ** attempt)
            logging.warning(
                "API error (attempt %d/%d): %s. Retrying in %.0fs.",
                attempt + 1, MAX_API_RETRIES, exc, wait,
            )
            time.sleep(wait)
    raise last_exc


# ---------- JSON helpers ----------

_REPAIR_PROMPT = (
    "Your previous response was not valid JSON. "
    "Return only the JSON object — no markdown fences, no explanation, nothing else."
)


def _parse_json(text: str) -> dict:
    """Parse JSON, tolerating accidental markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        inner = text.splitlines()[1:]
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        text = "\n".join(inner)
    return json.loads(text)


def _validate_signal(obj: dict) -> list:
    errors = []
    for f in ("error_markers", "recognition_markers", "resistance", "register",
              "student_statement_type", "student_content_summary"):
        if f not in obj:
            errors.append(f"missing: {f!r}")
    for m in obj.get("error_markers", []):
        for f in ("type", "confidence", "evidence"):
            if f not in m:
                errors.append(f"error_marker missing: {f!r}")
    return errors


def _validate_summary(obj: dict) -> list:
    errors = []
    for f in ("errors_presented", "prakriyas_applied", "new_errors_surfaced",
              "regression_observed", "recognition_events", "notes"):
        if f not in obj:
            errors.append(f"missing: {f!r}")
    return errors


def _call_with_repair(system: str, messages: list, validate_fn, max_tokens: int) -> dict:
    """
    Call Claude expecting JSON. On parse or schema failure, send a repair
    message and retry once. Raises ValueError after two failures.
    """
    msgs = list(messages)
    for attempt in range(2):
        raw = _call_claude(system, msgs, max_tokens=max_tokens)
        try:
            obj = _parse_json(raw)
        except json.JSONDecodeError:
            if attempt == 0:
                msgs += [
                    {"role": "assistant", "content": raw},
                    {"role": "user", "content": _REPAIR_PROMPT},
                ]
                continue
            raise ValueError(f"Unparseable JSON after repair attempt:\n{raw}")

        schema_errors = validate_fn(obj)
        if not schema_errors:
            return obj
        if attempt == 0:
            msgs += [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": (
                    f"The JSON is missing required fields: {schema_errors}. "
                    "Return the corrected JSON only."
                )},
            ]
        else:
            raise ValueError(f"Schema invalid after repair: {schema_errors}\n{raw}")

    raise ValueError("JSON extraction failed unexpectedly")


# ---------- Three prompt calls ----------

def _extract_signal(utterance: str, directive: dict, transcript: list) -> dict:
    user_text = (
        f"Current directive:\n{json.dumps(directive, ensure_ascii=False, indent=2)}\n\n"
        f"Student says: \"{utterance}\""
    )
    return _call_with_repair(
        _prompt("signal_extractor"),
        [{"role": "user", "content": user_text}],
        _validate_signal,
        max_tokens=512,
    )


def _generate_response(
    directive: dict,
    corpus_units: list,
    transcript: list,
    utterance: str,
) -> str:
    prakriya_name = (directive.get("prakriya") or {}).get("primary", "")
    module_text = _prakriya_module_text(prakriya_name) if prakriya_name else ""

    units_block = ""
    if corpus_units:
        parts = []
        for u in corpus_units:
            translation = u.get("translation", "")
            sanskrit = u.get("sanskrit", "")
            uid = u.get("id", "")
            entry = f"[{uid}]"
            if sanskrit:
                entry += f"\n{sanskrit}"
            if translation:
                entry += f"\n{translation}"
            parts.append(entry)
        units_block = "\n\n".join(parts)

    recent = transcript[-4:] if len(transcript) > 4 else transcript
    transcript_block = "\n".join(
        f"{'Student' if t['role'] == 'student' else 'Teacher'}: {t['text']}"
        for t in recent
    )

    sections = [f"## Directive\n{json.dumps(directive, ensure_ascii=False, indent=2)}"]
    if module_text:
        sections.append(f"## Active prakriyā module\n{module_text}")
    if units_block:
        sections.append(f"## Corpus units\n{units_block}")
    if transcript_block:
        sections.append(f"## Recent transcript\n{transcript_block}")
    if utterance:
        sections.append(f"## Student's last statement\n\"{utterance}\"")
    else:
        sections.append("## Context\nSession is opening. Produce the teacher's first statement.")

    messages = [{"role": "user", "content": "\n\n".join(sections)}]
    return _call_claude(_prompt("response_generator"), messages, max_tokens=512)


def _summarize_session(transcript: list) -> dict:
    transcript_text = "\n".join(
        f"{'Student' if t['role'] == 'student' else 'Teacher'}: {t['text']}"
        for t in transcript
    )
    return _call_with_repair(
        _prompt("session_summarizer"),
        [{"role": "user", "content": f"## Session transcript\n{transcript_text}"}],
        _validate_summary,
        max_tokens=1024,
    )


# ---------- Corpus fetch ----------

def _fetch_corpus(directive: dict) -> list:
    routing = directive.get("corpus_routing", {})
    preferred = routing.get("preferred_unit_ids", [])
    if preferred:
        units = corpus_query.query_by_ids(preferred)
        if units:
            return units
    return corpus_query.query(
        prakriya=routing.get("prakriya"),
        pedagogical_stage=routing.get("pedagogical_stage"),
        adhikara_level=routing.get("adhikara_level"),
        ontological_scope=routing.get("ontological_scope"),
        limit=3,
    )


# ---------- Checkpoint ----------

def _ckpt_path(session_id: str) -> Path:
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    return CKPT_DIR / f"{session_id}.jsonl"


def _ckpt_append(path: Path, entry: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _ckpt_delete(path: Path) -> None:
    if path.exists():
        path.unlink()


# ---------- Session log ----------

def _log(session_id: str, entry: dict) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with (LOGS_DIR / f"{session_id}.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---------- Session close (shared by run and recover) ----------

def _close_session(
    student_id: str,
    session_id: str,
    transcript: list,
    ckpt: Path,
) -> None:
    print("\n[Summarising session…]")
    summary = _summarize_session(transcript)
    close_event = {
        "event_type": "session_close",
        "student_id": student_id,
        "session_id": session_id,
        "session_summary": summary,
    }
    result = sm_process(close_event)
    _log(session_id, {"type": "session_close", "summary": summary, "result": result})
    _ckpt_delete(ckpt)
    stage = result["longitudinal_state"]["stage"]
    print(f"[Session closed. Longitudinal stage: {stage}]")


# ---------- Public API ----------

def run_session(student_id: str, session_id: str = None) -> None:
    """Run an interactive session. Reads from stdin, writes to stdout."""
    if session_id is None:
        session_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    ckpt = _ckpt_path(session_id)

    directive = sm_process({
        "event_type": "session_open",
        "student_id": student_id,
        "session_id": session_id,
    })
    _ckpt_append(ckpt, {"type": "session_open", "directive": directive})
    _log(session_id, {"type": "session_open", "directive": directive})

    transcript: list = []
    corpus_units = _fetch_corpus(directive)
    opening = _generate_response(directive, corpus_units, transcript, "")
    print(f"\nTeacher: {opening}\n")
    transcript.append({"role": "teacher", "text": opening})
    _ckpt_append(ckpt, {"type": "turn", "teacher": opening})

    try:
        while True:
            try:
                raw = input("Student (or 'end'): ").strip()
            except EOFError:
                break
            if raw.lower() in ("end", "quit", "exit", ""):
                if raw.lower() in ("end", "quit", "exit"):
                    break
                continue

            transcript.append({"role": "student", "text": raw})
            signal = _extract_signal(raw, directive, transcript)
            _log(session_id, {"type": "signal", "utterance": raw, "signal": signal})

            directive = sm_process({
                "event_type": "signal",
                "student_id": student_id,
                "session_id": session_id,
                "signal": signal,
            })

            corpus_units = _fetch_corpus(directive)
            response = _generate_response(directive, corpus_units, transcript, raw)
            print(f"\nTeacher: {response}\n")
            transcript.append({"role": "teacher", "text": response})

            turn = {
                "type": "turn",
                "student": raw,
                "signal": signal,
                "directive": directive,
                "teacher": response,
            }
            _ckpt_append(ckpt, turn)
            _log(session_id, turn)

    finally:
        try:
            _close_session(student_id, session_id, transcript, ckpt)
        except Exception as exc:
            logging.error("Session close failed: %s. Checkpoint preserved at %s.", exc, ckpt)


def recover_session(student_id: str, session_id: str) -> None:
    """Reconstruct session_close from an orphaned checkpoint."""
    ckpt = _ckpt_path(session_id)
    if not ckpt.exists():
        raise FileNotFoundError(f"No checkpoint for session {session_id!r}")

    transcript: list = []
    with ckpt.open(encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            if entry["type"] == "turn":
                if "student" in entry:
                    transcript.append({"role": "student", "text": entry["student"]})
                if "teacher" in entry:
                    transcript.append({"role": "teacher", "text": entry["teacher"]})

    print(f"[Recovering session {session_id!r}: {len(transcript)} transcript entries]")
    _close_session(student_id, session_id, transcript, ckpt)
