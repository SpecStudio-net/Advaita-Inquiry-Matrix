"""
AIM — Advaita Inquiry Matrix
Streamlit chat interface.

Run locally:
    streamlit run aim_app.py

Deploy:
    Push to GitHub and connect to Streamlit Community Cloud.
    Add ANTHROPIC_API_KEY in the app's Secrets panel.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st

# ---------- Secrets → environment (Streamlit Cloud) -------------------------
# On Streamlit Community Cloud, secrets are in st.secrets rather than .env.
# We copy them into os.environ so the rest of the codebase reads them the
# same way whether running locally or in the cloud.

for _key in ("ANTHROPIC_API_KEY", "AIM_MODEL", "AIM_GUARDRAIL_MODEL"):
    if _key not in os.environ and _key in st.secrets:
        os.environ[_key] = st.secrets[_key]

# ---------- Late imports (after env vars are set) ---------------------------

from engine.state_machine import process as sm_process
from llm_session import (
    _extract_signal,
    _fetch_corpus,
    _generate_response,
    _guardrail_check,
    _summarize_session,
    _log,
    _ckpt_append,
    _ckpt_delete,
    _ckpt_path,
    LOGS_DIR,
)

# ---------- Page config -----------------------------------------------------

st.set_page_config(page_title="AIM", page_icon="🪔", layout="centered")

# ---------- Login / consent screen ------------------------------------------
# Shown before anything else. Sets st.session_state.user_name on acceptance.

if "user_name" not in st.session_state:
    st.title("AIM — Advaita Inquiry Matrix")
    st.markdown(
        "AIM is a structured inquiry system in the Advaita Vedānta teaching "
        "tradition. It diagnoses the specific form of misidentification that is "
        "active and selects the appropriate classical teaching method in response."
    )
    st.divider()

    with st.form("login_form"):
        st.subheader("Before you begin")
        name = st.text_input(
            "Your name",
            placeholder="How would you like to be addressed?",
            help="Used to identify your session. No account required.",
        )

        st.info(
            "**Testing notice** \n\n"
            "AIM is currently in a testing phase. Your conversation — including "
            "every exchange with the teaching engine — will be logged and reviewed "
            "by the development team for the sole purpose of improving the system. "
            "Logs are not shared with third parties. \n\n"
            "If you have questions about data handling, contact "
            "hello@specstudio.net before beginning."
        )

        agreed = st.checkbox(
            "I understand that my session will be logged for testing and evaluation purposes."
        )

        submitted = st.form_submit_button("Begin", type="primary")

        if submitted:
            if not name.strip():
                st.error("Please enter your name to continue.")
            elif not agreed:
                st.error("Please acknowledge the testing notice to continue.")
            else:
                st.session_state.user_name = name.strip()
                st.rerun()

    st.stop()

# ---------- Resolved student ID (post-login) --------------------------------

STUDENT_ID = st.session_state.user_name

# ---------- Session state defaults ------------------------------------------

for key, default in {
    "active":           False,
    "messages":         [],
    "transcript":       [],
    "directive":        {},
    "session_id":       "",
    "show_engine":      False,
    "session_log_path": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- Engine panel renderer -------------------------------------------

def _render_engine_panel(signal: dict, directive: dict, guardrail: dict | None = None) -> None:
    with st.expander("Engine", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Signal**")
            markers = signal.get("error_markers", [])
            if markers:
                for m in markers:
                    st.markdown(
                        f"- `{m['type']}` · **{m['confidence']}**  \n"
                        f"  _{m.get('evidence', '')}_ "
                    )
            else:
                st.markdown("_no error markers_")

            rec = signal.get("recognition_markers", [])
            if rec:
                st.markdown("**Recognition**")
                for r in rec:
                    st.markdown(f"- {r}")

            res = signal.get("resistance", {})
            if res.get("present"):
                st.markdown(f"**Resistance:** {res.get('type', '—')}")

        with col2:
            st.markdown("**Directive**")
            sd = directive.get("session_directive", {})
            ls = directive.get("longitudinal_state", {})
            prakriya = directive.get("prakriya") or {}
            intervention = directive.get("intervention", {})

            st.markdown(f"- Stage: `{ls.get('stage', '—')}`")
            st.markdown(f"- Type: `{sd.get('type', '—')}`")
            if sd.get("probe_target"):
                st.markdown(f"- Probe: `{sd['probe_target']}`")
            if sd.get("redirect_domain"):
                st.markdown(f"- Redirect: `{sd['redirect_domain']}`")
            if prakriya.get("primary"):
                st.markdown(f"- Prakriyā: `{prakriya['primary']}`")
            if intervention:
                st.markdown(
                    f"- Tone: `{intervention.get('tone')}` · "
                    f"Challenge: `{intervention.get('challenge_level')}`"
                )

        if guardrail is not None:
            if guardrail.get("ok"):
                st.markdown("**Guardrail** ✓ _no violations_")
            else:
                st.markdown(f"**Guardrail** ⚠ {len(guardrail['violations'])} violation(s)")
                for v in guardrail["violations"]:
                    colour = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                        v.get("severity", "medium"), "🟡"
                    )
                    st.markdown(f"{colour} `{v['type']}` — _{v.get('evidence', '')}_ ")


# ---------- Sidebar ---------------------------------------------------------

with st.sidebar:
    st.header("Session")
    st.caption(f"Signed in as **{STUDENT_ID}**")

    if not st.session_state.active:
        if st.button("Start Session", type="primary"):
            session_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
            st.session_state.session_id = session_id
            st.session_state.messages = []
            st.session_state.transcript = []
            st.session_state.session_log_path = None

            with st.spinner("Opening session…"):
                directive = sm_process({
                    "event_type": "session_open",
                    "student_id": STUDENT_ID,
                    "session_id": session_id,
                })
                ckpt = _ckpt_path(session_id)
                _ckpt_append(ckpt, {"type": "session_open", "directive": directive})
                _log(session_id, {"type": "session_open", "directive": directive})

                corpus_units = _fetch_corpus(directive)
                opening = _generate_response(directive, corpus_units, [], "")

            st.session_state.directive = directive
            st.session_state.transcript.append({"role": "teacher", "text": opening})
            st.session_state.messages.append({
                "role":      "assistant",
                "content":   opening,
                "directive": directive,
            })
            st.session_state.active = True
            st.rerun()

        # Session log download (available after a session has been closed)
        if st.session_state.session_log_path:
            log_path = Path(st.session_state.session_log_path)
            if log_path.exists():
                st.divider()
                st.download_button(
                    label="Download session log",
                    data=log_path.read_bytes(),
                    file_name=log_path.name,
                    mime="application/x-ndjson",
                    help="Your session log in JSONL format. "
                         "You may be asked to share this with the development team.",
                )

        st.divider()
        if st.button("Sign out", type="tertiary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    else:
        stage = st.session_state.directive.get("longitudinal_state", {}).get("stage", "—")
        st.write(f"**Stage:** `{stage}`")
        st.divider()

        st.session_state.show_engine = st.toggle(
            "Show engine internals", value=st.session_state.show_engine
        )
        st.divider()

        if st.button("End Session", type="secondary"):
            with st.spinner("Summarising session…"):
                summary = _summarize_session(st.session_state.transcript)
                result = sm_process({
                    "event_type":      "session_close",
                    "student_id":      STUDENT_ID,
                    "session_id":      st.session_state.session_id,
                    "session_summary": summary,
                })
                _log(st.session_state.session_id, {
                    "type": "session_close", "summary": summary, "result": result,
                })
                _ckpt_delete(_ckpt_path(st.session_state.session_id))

            # Remember the log path so the download button appears
            log_path = LOGS_DIR / f"{st.session_state.session_id}.jsonl"
            st.session_state.session_log_path = str(log_path)

            final_stage = result["longitudinal_state"]["stage"]
            st.session_state.messages.append({
                "role":    "assistant",
                "content": f"*Session closed. Longitudinal stage: **{final_stage}**.*",
            })
            st.session_state.active = False
            st.rerun()

# ---------- Main area title -------------------------------------------------

st.title("AIM — Advaita Inquiry Matrix")

# ---------- Chat display ----------------------------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
    if st.session_state.show_engine and "signal" in msg:
        _render_engine_panel(msg["signal"], msg["directive"], msg.get("guardrail"))

# ---------- Chat input ------------------------------------------------------

if st.session_state.active:
    if user_input := st.chat_input("Your response…"):

        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.transcript.append({"role": "student", "text": user_input})
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            with st.spinner(""):
                signal = _extract_signal(
                    user_input,
                    st.session_state.directive,
                    st.session_state.transcript,
                )
                _log(st.session_state.session_id, {
                    "type": "signal", "utterance": user_input, "signal": signal,
                })

                st.session_state.directive = sm_process({
                    "event_type": "signal",
                    "student_id": STUDENT_ID,
                    "session_id": st.session_state.session_id,
                    "signal":     signal,
                })

                corpus_units = _fetch_corpus(st.session_state.directive)
                response = _generate_response(
                    st.session_state.directive,
                    corpus_units,
                    st.session_state.transcript,
                    user_input,
                )

                # Post-generation guardrail (soft — logs, never blocks)
                guardrail = _guardrail_check(response, st.session_state.directive)
                if not guardrail["ok"]:
                    _log(st.session_state.session_id, {
                        "type": "guardrail", **guardrail,
                    })

            st.markdown(response)

        if st.session_state.show_engine:
            _render_engine_panel(signal, st.session_state.directive, guardrail)

        st.session_state.transcript.append({"role": "teacher", "text": response})
        st.session_state.messages.append({
            "role":      "assistant",
            "content":   response,
            "signal":    signal,
            "directive": st.session_state.directive,
            "guardrail": guardrail,
        })

        turn = {
            "type":      "turn",
            "student":   user_input,
            "signal":    signal,
            "directive": st.session_state.directive,
            "teacher":   response,
            "guardrail": guardrail,
        }
        _ckpt_append(_ckpt_path(st.session_state.session_id), turn)
        _log(st.session_state.session_id, turn)
