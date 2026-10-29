"""IndicWrite Streamlit application: genuine IndicXlit inference only."""

from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st

from indicwrite.core import InputError, ModelOutputError, parse_preserve_terms, transliterate_text
from indicwrite.engine import load_indicxlit
from indicwrite.language_services import generate_hindi_gec, generate_english

st.set_page_config(page_title="IndicWrite • Hinglish to Hindi", page_icon="✍️", layout="wide")

st.markdown(
    """
    <style>
    :root {color-scheme: light;}
    .stApp {background: radial-gradient(circle at 86% 8%, #e6ebff 0, transparent 26%),
                        linear-gradient(150deg, #f8faff 0%, #f7f5ff 100%); color: #1b2140;}
    .block-container {max-width: 1100px; padding-top: 2.5rem; padding-bottom: 4rem;}
    .hero {padding: 1.5rem 0 1.35rem;}
    .eyebrow {letter-spacing: .18em; font-size: .76rem; font-weight: 800; color: #5d55c5;}
    .hero h1 {font-size: clamp(2.5rem, 6vw, 4.5rem); line-height:1.07; color: #222a54; margin: .65rem 0;}
    .hero p {font-size: 1.08rem; color: #525b78; max-width: 740px; line-height:1.7;}
    .panel {border-radius: 18px; padding: 1.15rem 1.45rem; background: #ffffffd9;
            border: 1px solid #dde1f1; box-shadow: 0 10px 25px #27305b0c;}
    .mini {font-size: .76rem; color: #526082; font-weight: 650; letter-spacing: .06em;}
    .info {color: #515d78; font-size:.88rem; line-height:1.6;}
    div.stButton > button[kind="primary"] {background: #504ac4; border-color: #504ac4;
             border-radius: 10px; min-height: 2.8rem; font-weight: 700;}
    div[data-testid="stTextArea"] textarea {background: white; border-radius: 12px; font-size: 1.04rem;}
    @media (max-width: 700px) {.block-container {padding-top: 1rem;} .hero {padding-top: 0.3rem;}}
    </style>
    """,
    unsafe_allow_html=True,
)

ENABLE_LANGUAGE_SERVICES = os.environ.get("INDICWRITE_ENABLE_LANGUAGE_SERVICES") == "1"
ENABLE_GEC_EXPERIMENTAL = os.environ.get("INDICWRITE_ENABLE_GEC_EXPERIMENTAL") == "1"

EXAMPLES = (
    "kal mujhe college jana hai",
    "aaj mausam bahut accha hai!",
    "namaste dosto, aap kaise ho?",
)


def clear_result() -> None:
    st.session_state["converted_text"] = ""
    st.session_state["improved_text"] = ""
    st.session_state["english_text"] = ""


def choose_example(value: str) -> None:
    st.session_state["source_text"] = value
    clear_result()


def reset() -> None:
    st.session_state["source_text"] = ""
    clear_result()


st.session_state.setdefault("source_text", "")
st.session_state.setdefault("converted_text", "")
st.session_state.setdefault("improved_text", "")
st.session_state.setdefault("english_text", "")

st.markdown(
    '<div class="hero"><div class="eyebrow">INDICWRITE / AI4BHARAT</div>'
    '<h1>Express yourself.<br>In your own script.</h1>'
    '<p>Write naturally in Roman Hindi and convert to Devanagari with the '
    '<b>real IndicXlit neural transliteration model</b>. '
    'No simulated AI responses, no hidden cloud API.</p></div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2, gap="large")
with col1:
    st.markdown("#### Your Hinglish text")
    st.text_area(
        "Roman Hindi", key="source_text",
        height=190, max_chars=500, on_change=clear_result,
        placeholder="kal mujhe college jana hai...",
        label_visibility="collapsed",
    )
    protected = st.text_input(
        "Keep English words unchanged (optional, comma-separated)",
        placeholder="Python, assignment, email",
        help="Hinglish is ambiguous; write words here that must remain in English.",
    )
    a, b = st.columns([2, 1])
    with a:
        convert = st.button("✦ Convert to Hindi", type="primary", use_container_width=True)
    with b:
        st.button("Clear", use_container_width=True, on_click=reset)
    st.caption("Examples")
    for i, example in enumerate(EXAMPLES):
        st.button(example, key=f"example_{i}", on_click=choose_example, args=(example,), use_container_width=True)

with col2:
    st.markdown("#### Your Devanagari result")
    if convert:
        clear_result()
        try:
            if not st.session_state["source_text"].strip():
                raise InputError("Enter a Roman-Hindi sentence to continue.")
            with st.spinner("Loading AI4Bharat IndicXlit and converting…"):
                model = load_indicxlit()
                st.session_state["converted_text"] = transliterate_text(
                    st.session_state["source_text"],
                    model,
                    preserve_terms=parse_preserve_terms(protected),
                )
        except (InputError, ModelOutputError) as exc:
            st.session_state["converted_text"] = ""
            st.warning(str(exc))
        except Exception as exc:
            st.session_state["converted_text"] = ""
            st.error("IndicXlit inference could not run. No substitute output was generated.")
            with st.expander("Technical error details"):
                st.exception(exc)
    if st.session_state["converted_text"]:
        st.success("Generated by IndicXlit")
        st.code(st.session_state["converted_text"], language=None, wrap_lines=True)
        st.caption("Use the copy icon in the output box to copy the result.")
        st.download_button(
            "Download result (.txt)", data=st.session_state["converted_text"],
            file_name="indicwrite-hindi.txt", mime="text/plain",
        )
    else:
        st.info("Your generated Hindi text will appear here after conversion.")
    if st.session_state["converted_text"]:
        st.divider()
        st.markdown("##### Smart writing tools")
        if ENABLE_LANGUAGE_SERVICES:
            st.caption("Optional real, locally running checkpoints: MIT Hindi mT5 grammar correction and Apache-2.0 OPUS-MT English translation. Neither is BharatGen or IndicTrans2. First load downloads weights; review all edits for accuracy.")
            a, b = st.columns(2)
            with a:
                improve = st.button("Improve Hindi grammar (research)", use_container_width=True, disabled=not ENABLE_GEC_EXPERIMENTAL)
            with b:
                translate = st.button("Translate to English", use_container_width=True)
            if not ENABLE_GEC_EXPERIMENTAL:
                st.caption("Grammar model is disabled pending quality verification: the first checkpoint produced Bengali/mixed-script predictions.")
            if improve:
                try:
                    with st.spinner("Running the Hindi mT5 grammar model…"):
                        st.session_state["improved_text"] = generate_hindi_gec(st.session_state["converted_text"])
                except Exception as exc:
                    st.session_state["improved_text"] = ""
                    st.error(f"Hindi grammar model unavailable: {exc}")
            if translate:
                try:
                    with st.spinner("Running the OPUS-MT translation model…"):
                        st.session_state["english_text"] = generate_english(st.session_state["converted_text"])
                except Exception as exc:
                    st.session_state["english_text"] = ""
                    st.error(f"English translation model unavailable: {exc}")
            if st.session_state["improved_text"]:
                st.caption("Hindi mT5 grammar model output — may change the meaning; compare before using")
                st.code(st.session_state["improved_text"], language=None, wrap_lines=True)
            if st.session_state["english_text"]:
                st.caption("English output — Helsinki-NLP OPUS-MT, not IndicTrans2")
                st.code(st.session_state["english_text"], language=None, wrap_lines=True)
        else:
            st.caption("Optional grammar correction and English translation are off in this environment. They require separately installed language model dependencies and INDICWRITE_ENABLE_LANGUAGE_SERVICES=1.")

    st.markdown(
        '<div class="panel"><span class="mini">MODEL</span><br>'
        '<strong>AI4Bharat IndicXlit · Hindi (hi)</strong>'
        '<p class="info">Official pretrained Roman-to-Indic transliteration. '
        'Punctuation, numbers and existing Hindi script are preserved. '
        'English loanwords may need explicit preservation.</p></div>',
        unsafe_allow_html=True,
    )

st.divider()
st.markdown("##### Model transparency")
st.caption("Core: AI4Bharat IndicXlit (verified). Optional writing: independent Hindi mT5 grammar model and Helsinki OPUS-MT translation; enable separately. BharatGen Param-1 is a restricted academic research option, not integrated or model-verified. IndicTrans2 requires HF terms acceptance and is not integrated.")
st.caption("CS3235 • Working with LLMs • Munnaluri Rishikesh • 1RVU23CSE291")
