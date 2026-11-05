"""IndicWrite Streamlit application: genuine IndicXlit inference only."""

from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st

from indicwrite.core import InputError, ModelOutputError, parse_preserve_terms, transliterate_text, validate_text, has_convertible_tokens
from indicwrite.engine import load_indicxlit
from indicwrite.language_services import generate_hindi_gec, generate_english
from indicwrite.private_bharatgen import private_research_enabled, run_private_research

st.set_page_config(page_title="IndicWrite • Write Hindi, Your Way", page_icon="✍️", layout="wide")

st.markdown(
    """
    <style>
    :root { color-scheme: light; }
    .stApp {
        color: #27243e;
        background:
            radial-gradient(ellipse 44% 36% at 96% 3%, #e8e0ff 0%, transparent 100%),
            radial-gradient(ellipse 42% 28% at 0% 30%, #f0ecff 0%, transparent 100%),
            #faf9ff;
    }
    header[data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 1240px; padding: 1.25rem 2rem 4rem; }
    .brandbar { display: flex; align-items: center; justify-content: space-between;
        gap: 1rem; padding: .45rem 0 1.2rem; border-bottom: 1px solid #e9e4f3; }
    .brand { display: flex; align-items: center; gap: .8rem; font-size: 1.28rem;
        font-weight: 850; letter-spacing: -.055em; color: #27233e; }
    .brandmark { width: 42px; height: 42px; border-radius: 13px; display: grid;
        place-items: center; background: #7359d0; color: white; font-size: 1.5rem;
        font-weight: 700; letter-spacing: 0; box-shadow: 0 5px 16px #7259cb36; }
    .brand-accent { color: #7259ce; }
    .brand-status { font-size: .75rem; color: #655d81; font-weight: 700;
        border: 1px solid #e5def6; background: #ffffffca; padding: .52rem .8rem;
        border-radius: 999px; white-space: nowrap; }
    .brand-status::before { content: ""; display: inline-block; width: 7px;
        height: 7px; border-radius: 50%; margin-right: 7px; background: #4b987f; }
    .hero { text-align: center; max-width: 810px; margin: 3.25rem auto 2.5rem; }
    .eyebrow { display: inline-flex; padding: .53rem .9rem; border-radius: 999px;
        border: 1px solid #e5def5; background: #ffffffda; color: #6755aa;
        letter-spacing: .11em; font-size: .68rem; font-weight: 850; }
    .hero h1 { font-size: clamp(2.45rem, 5.8vw, 4.35rem);
        line-height: 1.12; letter-spacing: -.055em;
        color: #292440; font-weight: 850; margin: 1.15rem auto .95rem; }
    .hero h1 em { font-style: normal; color: #795dcf; }
    .hero p { font-size: 1rem; line-height: 1.8; color: #645e7a;
        max-width: 650px; margin: 0 auto; }
    .hero-points { display: flex; flex-wrap: wrap; justify-content: center;
        gap: .55rem; margin-top: 1.25rem; }
    .hero-points span { font-size: .72rem; font-weight: 750; color: #645c85;
        background: #f0ecfc; border: 1px solid #e9e2fa;
        border-radius: 999px; padding: .37rem .75rem; }
    /* Target only the workspace pair; keep nested action buttons unboxed. */
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] h2)
      > div[data-testid="stColumn"] {
        min-width: 0; padding: 1.25rem 1.4rem 1.5rem;
        background: #fff; border: 1px solid #e9e5f1;
        border-radius: 22px; box-shadow: 0 13px 34px #3324570d;
    }
    div[data-testid="stColumn"] h2 { font-size: 1.34rem;
        color: #2f2947; letter-spacing: -.035em; margin-bottom: 1rem; }
    div[data-testid="stColumn"] h3 { font-size: 1.1rem; color: #302847; }
    div[data-testid="stColumn"] [data-testid="stCaptionContainer"] p {
        color: #6c6480; font-size: .78rem; line-height: 1.55; }
    div[data-testid="stTextArea"] textarea {
        border-radius: 13px; background: #fcfbff;
        border: 1px solid #ddd6ee; font-size: 1.05rem;
        line-height: 1.7; color: #29243f; }
    div[data-testid="stTextInput"] input {
        border-radius: 11px; background: #fcfbff; border-color: #ddd6ee; }
    div[data-testid="stTextArea"] textarea:focus,
    div[data-testid="stTextInput"] input:focus {
        border-color: #7560cf; box-shadow: 0 0 0 3px #7964ca24; }
    div.stButton button { min-height: 2.65rem; border-radius: 10px;
        font-weight: 720; white-space: normal; border-color: #e6e0f2;
        color: #55468b; background: #f9f7ff; }
    div.stButton button:hover { border-color: #927ce4; color: #4e3a9a; }
    div.stButton button[kind="primary"] {
        background: #745ad3; border-color: #745ad3; color: #fff;
        font-weight: 800; box-shadow: 0 5px 14px #735ad02b; }
    div.stButton button[kind="primary"]:hover {
        background: #6347c0; border-color: #6347c0; color: #fff; }
    div.stButton button:focus-visible, div[data-testid="stDownloadButton"] button:focus-visible {
        outline: 3px solid #947bea; outline-offset: 3px; }
    div[data-testid="stDownloadButton"] button { min-height: 2.55rem;
        border-radius: 10px; font-weight: 700; }
    div[data-testid="stCode"] pre { background: #f8f6ff;
        border: 1px solid #ebe5fa; border-radius: 13px;
        font-size: 1.15rem; line-height: 1.8; white-space: pre-wrap;
        overflow-wrap: anywhere; }
    div[data-testid="stAlert"] { border-radius: 12px; }
    .panel { border-radius: 15px; padding: 1rem 1.15rem;
        background: #f7f4ff; border: 1px solid #e7e0f8; margin-top: 1rem; }
    .mini { font-size: .7rem; font-weight: 850; letter-spacing: .12em;
        color: #6655aa; }
    .info { color: #605879; font-size: .8rem; line-height: 1.65;
        margin: .4rem 0 0; }
    .footer-note { text-align: center; font-size: .78rem;
        color: #756d8a; padding: .45rem 0 1rem; }
    @media (max-width: 800px) {
        .block-container { padding: 1rem 1rem 2.5rem; }
        .hero { margin: 2rem auto 1.75rem; }
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] h2) {
            flex-wrap: wrap; flex-direction: column; gap: 1rem !important;
        }
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] h2)
          > div[data-testid="stColumn"] {
            width: 100% !important; flex: 1 1 100% !important;
        }
    }
    @media (max-width: 390px) {
        .block-container { padding-left: .65rem; padding-right: .65rem; }
        .brand { font-size: 1.12rem; }
        .brandmark { width: 35px; height: 35px; }
        .brand-status { font-size: .63rem; padding: .42rem .55rem; }
        .hero { margin: 1.55rem auto 1.45rem; }
        .hero h1 { font-size: 2.35rem; }
        .hero p { font-size: .89rem; }
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] h2)
          > div[data-testid="stColumn"] { padding: 1rem .85rem; }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { scroll-behavior: auto !important;
            transition-duration: .01ms !important; animation-duration: .01ms !important; }
    }
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
    st.session_state["human_edit"] = ""
    st.session_state["did_transliterate"] = False
    st.session_state["private_bharatgen_suggestion"] = None
    st.session_state["private_bharatgen_reviewed"] = False


def choose_example(value: str) -> None:
    st.session_state["source_text"] = value
    clear_result()


def reset() -> None:
    st.session_state["source_text"] = ""
    st.session_state["preserve_raw"] = ""
    clear_result()


st.session_state.setdefault("source_text", "")
st.session_state.setdefault("converted_text", "")
st.session_state.setdefault("improved_text", "")
st.session_state.setdefault("english_text", "")
st.session_state.setdefault("human_edit", "")
st.session_state.setdefault("did_transliterate", False)
st.session_state.setdefault("preserve_raw", "")
st.session_state.setdefault("private_bharatgen_suggestion", None)
st.session_state.setdefault("private_bharatgen_reviewed", False)

st.markdown(
    '<div class="brandbar"><div class="brand"><span class="brandmark" aria-hidden="true">इ</span>'
    '<span>Indic<span class="brand-accent">Write</span></span></div>'
    '<span class="brand-status">Official checkpoint · Native app</span></div>'
    '<section class="hero" aria-label="About IndicWrite">'
    '<span class="eyebrow">AI4BHARAT INDICXLIT · ROMAN HINDI → देवनागरी</span>'
    '<h1>Your words, <em>beautifully</em><br> written in Hindi.</h1>'
    '<p>Type naturally in Hinglish. Convert to Devanagari with the genuine '
    'pretrained AI4Bharat IndicXlit model — keeping punctuation, numbers, '
    'and the English words you choose intact.</p>'
    '<div class="hero-points"><span>✦ Genuine neural inference</span>'
    '<span>✓ Editable &amp; copyable</span><span>↓ UTF-8 downloads</span></div>'
    '</section>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2, gap="large")
with col1:
    st.caption("01 · INPUT")
    st.markdown("## Your Hinglish")
    st.text_area(
        "Roman Hindi", key="source_text",
        height=190, max_chars=500, on_change=clear_result,
        placeholder="kal mujhe college jana hai...",
        label_visibility="visible",
    )
    protected = st.text_input(
        "Keep English words unchanged (optional, comma-separated)",
        key="preserve_raw", on_change=clear_result,
        placeholder="Python, assignment, email",
        help="Hinglish is ambiguous; write words here that must remain in English.",
    )
    a, b = st.columns([2, 1])
    with a:
        convert = st.button("Convert to Hindi", type="primary", use_container_width=True)
    with b:
        st.button("Clear", use_container_width=True, on_click=reset)
    st.caption("TRY AN EXAMPLE")
    for i, example in enumerate(EXAMPLES):
        st.button(example, key=f"example_{i}", on_click=choose_example, args=(example,), use_container_width=True)

with col2:
    st.caption("02 · OUTPUT")
    st.markdown("## Your Devanagari")
    if convert:
        clear_result()
        try:
            text = st.session_state["source_text"]
            tokens = validate_text(text)
            preserve_terms = parse_preserve_terms(protected)
            requires_model = has_convertible_tokens(tokens, preserve_terms)
            if requires_model:
                with st.spinner("Initializing genuine AI4Bharat IndicXlit (first cloud conversion may install dependencies and download official weights)…"):
                    model = load_indicxlit()
                    result = transliterate_text(text, model, preserve_terms=preserve_terms)
            else:
                result = transliterate_text(text, None, preserve_terms=preserve_terms)
            st.session_state["converted_text"] = result
            st.session_state["did_transliterate"] = requires_model
        except (InputError, ModelOutputError) as exc:
            st.session_state["converted_text"] = ""
            st.warning(str(exc))
        except Exception as exc:
            st.session_state["converted_text"] = ""
            st.error("IndicXlit inference could not run. No substitute output was generated.")
            if os.environ.get("INDICWRITE_DEBUG") == "1":
                with st.expander("Technical error details (development only)"):
                    st.exception(exc)
            else:
                st.caption("Technical details are hidden in public mode. Check server logs.")
    if st.session_state["converted_text"]:
        st.success("Generated by IndicXlit" if st.session_state["did_transliterate"] else "No Roman-Hindi words required conversion; text kept unchanged.")
        st.code(st.session_state["converted_text"], language=None, wrap_lines=True)
        st.caption("Use the code-block copy icon, or download the original UTF-8 result below.")
        if not st.session_state["human_edit"]:
            st.session_state["human_edit"] = st.session_state["converted_text"]
        with st.expander("Review and refine Hindi manually", expanded=False):
            st.caption("Human-edited draft: this is NOT an AI grammar correction. Check grammar and meaning yourself.")
            st.text_area("Editable Hindi", key="human_edit", height=130)
            st.download_button(
                "Download reviewed Hindi (.txt)",
                data=st.session_state["human_edit"],
                file_name="indicwrite-reviewed-hindi.txt",
                mime="text/plain",
            )
        st.download_button(
            "Download result (.txt)", data=st.session_state["converted_text"],
            file_name="indicwrite-hindi.txt", mime="text/plain",
        )
    else:
        st.info("Your generated Hindi text will appear here after conversion.")
    if st.session_state["converted_text"]:
        st.divider()
        st.markdown("### Smart writing tools")
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

    # This section is entirely opt-in and refuses non-loopback hosting.
    research_requested = os.environ.get("INDICWRITE_PRIVATE_BHARATGEN") == "1"
    if research_requested and st.session_state["converted_text"]:
        bind_address = st.get_option("server.address")
        enabled = private_research_enabled(server_address=bind_address)
        st.divider()
        st.markdown("### Private BharatGen research (T4 GPU required)")
        st.caption(
            "Experimental BharatGen Param-1-2.9B-Instruct (research license). "
            "Private localhost only. Suggestions are NOT validated corrections, "
            "and are never applied automatically. The ~6.3 GiB GPU model loads on demand."
        )
        if not enabled:
            st.warning(
                "Research mode locked: launch Streamlit on 127.0.0.1 and set all "
                "three explicit acknowledgement environment flags. Never use this "
                "mode in a public hosted deployment."
            )
        else:
            if st.button("Generate private BharatGen suggestion", use_container_width=True):
                st.session_state["private_bharatgen_suggestion"] = None
                st.session_state["private_bharatgen_reviewed"] = False
                try:
                    with st.spinner("Loading verified pinned BharatGen checkpoint and generating…"):
                        st.session_state["private_bharatgen_suggestion"] = run_private_research(
                            st.session_state["converted_text"], server_address=bind_address
                        )
                except Exception:
                    st.error("Private research inference failed; original text is unchanged. Review local console logs.")
            suggestion = st.session_state["private_bharatgen_suggestion"]
            if suggestion:
                st.caption("Pretrained model suggestion — compare with the original before using.")
                st.code(suggestion["candidate"], language=None, wrap_lines=True)
                for warning in suggestion["warnings"]:
                    st.warning(warning)
                st.checkbox(
                    "I have compared the original and suggestion for meaning, names and factual accuracy.",
                    key="private_bharatgen_reviewed",
                )
                if st.session_state["private_bharatgen_reviewed"]:
                    st.download_button(
                        "Download reviewed suggestion (private)",
                        suggestion["candidate"], file_name="indicwrite-private-suggestion.txt",
                        mime="text/plain",
                    )

    st.markdown(
        '<div class="panel"><span class="mini">MODEL</span><br>'
        '<strong>AI4Bharat IndicXlit · Hindi (hi)</strong>'
        '<p class="info">Official pretrained Roman-to-Indic transliteration. '
        'Punctuation, numbers and existing Hindi script are preserved. '
        'English loanwords may need explicit preservation.</p></div>',
        unsafe_allow_html=True,
    )

st.divider()
st.markdown("## Model transparency")
st.caption("Core: AI4Bharat IndicXlit (verified). Optional writing: independent Hindi mT5 grammar model and Helsinki OPUS-MT translation; enable separately. BharatGen Param-1 was genuinely executed in a private T4 Colab research run (1 smoke + 10 cases), and is only available through explicit local opt-in; not on public deployments. IndicTrans2 requires HF terms acceptance and is not integrated.")
st.markdown('<div class="footer-note">CS3235 · Working with LLMs · RV University · Munnaluri Rishikesh · 1RVU23CSE291</div>', unsafe_allow_html=True)
