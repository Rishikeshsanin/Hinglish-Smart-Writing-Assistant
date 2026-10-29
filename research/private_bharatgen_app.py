"""Private BharatGen academic research UI for Python 3.12 + CUDA.

Independent of Streamlit/IndicXlit's legacy Python 3.10 / Fairseq stack.
Never bind to public network interfaces. No cloud model API or text storage.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import streamlit as st
from indicwrite.private_bharatgen import private_research_enabled, run_private_research

st.set_page_config(page_title="IndicWrite · Private BharatGen Research", layout="centered")


def reset_private_result() -> None:
    st.session_state["candidate"] = None
    st.session_state["review_confirmed"] = False


st.session_state.setdefault("hindi_source", "")
st.session_state.setdefault("candidate", None)
st.session_state.setdefault("review_confirmed", False)

st.title("IndicWrite · Private BharatGen Research")
st.caption("Experimental, private academic text editing · Param-1-2.9B-Instruct · T4 GPU / FP16")

# Both explicit license/code acknowledgements and loopback server binding are mandatory.
bind = st.get_option("server.address")
if not private_research_enabled(server_address=bind):
    st.error(
        "Research UI locked. For local academic use only, bind Streamlit to 127.0.0.1 "
        "and explicitly authorize the three required environment flags. "
        "Never run this checkpoint on a publicly accessible Streamlit server."
    )
    st.stop()

st.warning(
    "The pretrained model is an experimental Hindi writing assistant, not a verified "
    "grammar authority. Compare all facts and meaning with the original. "
    "Public model/output distribution requires separate BharatGen license approval."
)

st.text_area(
    "Original Hindi (Devanagari)",
    key="hindi_source",
    height=150,
    max_chars=500,
    placeholder="वह लड़की रोज़ स्कूल जाता है।",
    on_change=reset_private_result,
)

a, b = st.columns([2, 1])
with a:
    generate = st.button("Generate research suggestion", type="primary", use_container_width=True)
with b:
    st.button("Clear", use_container_width=True, on_click=lambda: (
        st.session_state.update(hindi_source=""), reset_private_result()
    ))

if generate:
    reset_private_result()
    try:
        with st.spinner("Running pinned BharatGen checkpoint on the local GPU…"):
            st.session_state["candidate"] = run_private_research(
                st.session_state["hindi_source"], server_address=bind
            )
    except (ValueError, PermissionError, RuntimeError) as exc:
        st.error(str(exc))
    except Exception:
        st.error("Private GPU inference failed. No candidate was applied. Check local logs.")

record = st.session_state["candidate"]
if record:
    st.subheader("Model suggestion — not automatically applied")
    st.code(record["candidate"], language=None, wrap_lines=True)
    for warning in record["warnings"]:
        st.warning(warning)
    st.checkbox(
        "I checked the original and proposed sentences for facts, names, meaning and grammar.",
        key="review_confirmed",
    )
    if st.session_state["review_confirmed"]:
        st.download_button(
            "Download privately reviewed suggestion",
            data=record["candidate"],
            file_name="bharatgen-private-reviewed-hindi.txt",
            mime="text/plain",
        )
    else:
        st.caption("Review the suggestion before downloading. Generated words remain private.")

st.caption(
    "Source: BharatGen Param-1-2.9B-Instruct · Private pinned experimental GPU runtime. "
    "No output is sent to cloud APIs, written to files or committed to GitHub."
)
