"""
AIM — Advaita Inquiry Matrix
Streamlit chat interface.

Run with:
    streamlit run aim_app.py
"""

import getpass
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st

from engine.state_machine import process as sm_process
from llm_session import (
    _extract_signal,
    _fetch_corpus,
    _generate_response,
    _summarize_session,
    _log,
    _ckpt_append,
    _ckpt_delete,
    _ckpt_path,
)

# ---------- Page config ----------

st.set_page_config(page_title="AIM", page_icon="🪔", layout="centered")
st.title("AIM — Advaita Inquiry Matrix")

# ---------- Session state defaults ----------

STUDENT_ID = getpass.getuser()  # single-user assumption: system login name = student id

for key, default in {
    "active":      False,
    "messages":    [],
    "transcript":  [],
    "directive":   {},
    "session_id":  "",
    "show_engine": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- Engine panel renderer ----------

def _render_engine_panel(signal: dict, directive: dict) -> None:
    """Render a collapsible engine internals panel."""
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


# ---------- Sidebar ----------

with st.sidebar:
    st.header("Session")

    if not st.session_state.active:
        if st.button("Start Session", type="primary"):
            session_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
            st.session_state.session_id = session_id
            st.session_state.messages = []
            st.session_state.transcript = []

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

            final_stage = result["longitudinal_state"]["stage"]
            st.session_state.messages.append({
                "role":    "assistant",
                "content": f"*Session closed. Longitudinal stage: **{final_stage}**.*",
            })
            st.session_state.active = False
            st.rerun()

# ---------- Chat display ----------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
    if st.session_state.show_engine and "signal" in msg:
        _render_engine_panel(msg["signal"], msg["directive"])

# ---------- Chat input ----------

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

            st.markdown(response)

        if st.session_state.show_engine:
            _render_engine_panel(signal, st.session_state.directive)

        st.session_state.transcript.append({"role": "teacher", "text": response})
        st.session_state.messages.append({
            "role":      "assistant",
            "content":   response,
            "signal":    signal,
            "directive": st.session_state.directive,
        })

        turn = {
            "type":      "turn",
            "student":   user_input,
            "signal":    signal,
            "directive": st.session_state.directive,
            "teacher":   response,
        }
        _ckpt_append(_ckpt_path(st.session_state.session_id), turn)
        _log(st.session_state.session_id, turn)
