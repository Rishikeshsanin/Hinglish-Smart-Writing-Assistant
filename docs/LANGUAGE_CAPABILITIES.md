# IndicWrite language capabilities — Agent C review

Reviewed 2026-11-05 for issue #35. This document does not change the original
AI4Bharat IndicXlit runtime, its 40-case evaluation, cloud deployment or faculty
report. Real inference, mocked unit tests and independent human evaluation are
different kinds of evidence.

## Capability matrix

| Capability | Model | Prior evidence | Release gate |
| --- | --- | --- | --- |
| Roman Hindi → Devanagari | AI4Bharat IndicXlit | 40 actual model predictions in existing evaluation | Existing separately managed MVP |
| Hindi → English (optional) | Helsinki-NLP/opus-mt-hi-en (Apache-2.0) | Genuine two-sentence smoke in run 40876423545; real browser IndicXlit→OPUS flow in 40879090261 | Local supported-environment opt-in; **not** a full quality benchmark |
| Hindi grammar correction | manavdhamecha77/GEC-mT5-Small-Hindi and separately screened mT5/Qwen | Actual model trials failed quality review: script/meaning drift or limited corrections | Disabled as product feature |
| IndicTrans2 Indic→English | ai4bharat/indictrans2-indic-en-dist-200M (MIT card label) | **Not downloaded or executed**; checkpoint access gated | Disabled pending authorized access, code audit and real evaluation |
| Public BharatGen rewriting | bharatgenai/Param-1-2.9B-Instruct | Real private T4 generation of 1 smoke + 10 candidates, not independent linguistic certification | Disabled pending written public-output/hosting permission and quality review |
| Private BharatGen research | Same pinned Param-1 checkpoint | Pretrained GPU inference verified privately; **no full GPU browser UI test** | Local-only, explicit consent, separate Python 3.12 + GPU |

The historical smoke/QA references:
- https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40876423545
- https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40879090261

OPUS is **not** AI4Bharat IndicTrans2; transliteration metrics are not
translation metrics. Manual human editing is not neural grammar correction.

## Agent B integration: safe Python callable contract

Use src/indicwrite/language_services.py in any new UI integration.

- capability_status("opus_hi_en", environment=None): returns provider/model,
  explicit evidence limitations and enabled status without loading weights.
- translate_optional(hindi, environment=None, resources=None): raises
  LanguageFeatureDisabled **before any model load** unless the literal flag
  INDICWRITE_ENABLE_LANGUAGE_SERVICES=1 is present. In a supported opted-in
  environment it uses the genuine, lazy Helsinki OPUS-MT model, returning a
  dict with source, candidate, model_id, model_family, warnings,
  meaning_preservation="REQUIRES_HUMAN_REVIEW" and auto_apply=False.
- capability_status("hindi_gec"), capability_status("indictrans2") and
  capability_status("bharatgen_public") always return enabled=False.
  rewrite_optional() and translate_indictrans2() raise the explicit disabled
  exception even if legacy experimental flags are present.
- The original generate_english() and generate_hindi_gec() callable research
  paths are preserved for existing opt-in UI/test compatibility. The latter is
  **not** a verified correction feature. A unit-test fake resource is NOT a
  real model result and must never be marketed as one.

The shared preservation_warnings(source, candidate, translation=False)
compares Unicode numeric groups, Latin technical terms/names and Hindi
meaning-bearing cues (only in rewrite mode). A rewrite candidate with a wrong
script, changed numbers, missing Latin terms or lost cues is rejected.
Private BharatGen also uses these checks and rejects non-Hindi output.

**Heuristics are not a semantic proof.** They may miss different negation
phrases, swapped people/roles, amounts written as words, changed dates,
hallucinations or other meaning drift. Compare originals manually.
Translation cannot use Hindi negation-token matching on English output.

## Reproducible optional OPUS translation evaluation

The 12 authored, fixed Hindi examples in research/translation_cases.csv
cover questions, negation, uncertainty, gender, time, numbers and mixed Latin
terms. **No generated predictions or manual quality scores are committed.**

Only with a supported local environment, enough RAM, a working PyTorch
installation, and dependencies from requirements-language-services.txt,
explicitly authorize real public-checkpoint download:

~~~bash
PYTHONPATH=src python research/translation_eval.py --generate --allow-model-download
~~~

The script uses the actual loaded OPUS-MT checkpoint, or fails. It generates
all 12 before writing any CSV. Outputs, automatic preservation alerts and
latency are stored only under gitignored private_research/
(opus-mt-translation-review.csv and its metadata JSON). This command is NOT
claimed to have run in this PR. Neither cached examples nor stubbed outputs
may be submitted as generated model evidence.

Every candidate needs an actual bilingual human review:
- adequacy_score_1_to_5: whether all essential source meaning is preserved
  (1 critical distortion; 5 faithful)
- fluency_score_1_to_5: English naturalness/correctness (1 poor; 5 excellent)
- entities_numbers_preserved: true/false after checking all named entities,
  Latin terms, numeric data and time expressions
- invented_information: true/false for unsupported additions
- reviewer_id: real identifier, with any non-expert/student limitation disclosed

Then aggregate **only after filling all human scores**:

~~~bash
PYTHONPATH=src python research/translation_eval.py --summarize
~~~

This rejects missing/duplicate case IDs, incomplete scores, absent real-run
metadata and wrong model attribution. A summary JSON contains only counts,
means, rates and limitations, **not** full candidate sentences. Twelve authored
cases are screening evidence, not a production accuracy guarantee. Generated
sentences may not be saved to public docs or the faculty report by the script.

## Private BharatGen: current safeguards

The private helper requires all literal "1" flags:
INDICWRITE_PRIVATE_BHARATGEN,
INDICWRITE_REVIEWED_BHARATGEN_CODE,
INDICWRITE_ACKNOWLEDGE_BHARATGEN_LICENSE.
The server address must be a loopback bind (127.0.0.1, localhost or ::1);
do not tunnel, reverse-proxy or deploy publicly. The private model is pinned
to revision f9b32a727458727ff515fea5d82df00ae9b7ad56, with
custom-code SHA-256 prechecks before allowing remote code. Hashing is not
sandboxing. No model load occurs on import; suggestions are never auto-applied.

The historical BharatGen Research License explicitly required written
approval to publicly distribute outputs or host the model. Current model
metadata has conflicted with this history. **No BharatGen private output,
model weight, reviewer CSV, raw ZIP or screenshot may be committed or
published pending clarification.** Human review remains necessary even for
a warning-free suggestion. Private evidence generated previously on the
student's authorized T4 is not a new inference result in this PR. The full
private Streamlit GPU/browser flow is still unverified. See
docs/PRIVATE_BHARATGEN_UI.md and docs/PRIVATE_HUMAN_REVIEW.md.
No new GPU session or paid service was used in this workstream.

## IndicTrans2 feasibility and precise blocker

As checked on 2026-11-05, the official model page is MIT-labeled **but
still gated**: an authenticated Hugging Face account must agree to share
its account information with the model owner to access weights. The
correct direction is hin_Deva to eng_Latn, with IndicTransToolkit
pre/post-processing and Transformers custom code. A licensed developer with
authorized access must accept the terms personally, review and pin any
trusted remote code, provision a separate free runtime, and demonstrate
actual checkpoint inference and quality before enabling it.

Do not bypass the access gate, request/share credentials, infer that MIT
metadata confers automatic access, or silently use OPUS as IndicTrans2.
The model card also mentions newer Indic-Translate variants: these are
**not** executed or integrated either.

Sources:
- https://huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M
- https://huggingface.co/Helsinki-NLP/opus-mt-hi-en
- https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct/blame/13498f81c10fba9d716ea2969d00df3538c10ca7/LICENSE

## Test scope and unresolved external work

This branch adds deterministic unit-test contracts and research evaluation
protocols. **Mock tests do not imply real model execution.** This PR
performs no new public deployment or real neural inference. Historical
evidence remains historical.

Next, when properly authorized and with available free resources:
(1) run the 12-case OPUS evaluation using actual weights; (2) obtain a real
bilingual reviewer; (3) request IndicTrans2 access in the user's own account
and evaluate pinned inference; (4) obtain written BharatGen output
permissions and independent quality review before any public enablement.
Keep unsupported controls disabled until those gates are met.
