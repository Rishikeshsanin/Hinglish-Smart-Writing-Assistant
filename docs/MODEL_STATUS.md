# Model implementation and evidence status

Last reviewed: 2026-10-29. Real-model and browser evidence verified.

| Feature | Official checkpoint/package | Status |
| --- | --- | --- |
| Roman Hindi to Devanagari | AI4Bharat IndicXlit, `ai4bharat-transliteration==1.1.3` | Official neural inference **VERIFIED** on GitHub Actions (run 40870311669) |
| Hindi grammar rewriting | `bharatgenai/Param-1-2.9B-Instruct` at `f9b32a727458727ff515fea5d82df00ae9b7ad56` | **PRIVATE GPU pretrained inference VERIFIED**: 11 generations, full local-only UI end-to-end not yet tested; public use restricted |
| Hindi → English translation | `ai4bharat/indictrans2-indic-en-dist-200M` | Correct direction identified; gated checkpoint not accessed or executed |

## Historical IndicXlit inference verification

The initial runner installed the package and downloaded the 121 MB checkpoint but failed due to PyTorch 2.6+ restricted legacy Fairseq checkpoint loading. Scoped allowlisting of the official checkpoint's `argparse.Namespace` resolved this. Follow-up GitHub Actions run **40870311669** passed real inference on three sample sentences; run **40870722731** executed forty genuine predictions; run **40871267464** passed Chromium desktop/mobile UI checks. No mock results were used for these executed checks.

## Model considerations

- IndicXlit: ~11M transformer parameters, pretrained on Aksharantar, AI4Bharat repo MIT. Package release 1.1.3 uses legacy fairseq and may need a compatible Python/Linux stack; package metadata alone does not prove compatibility.
- BharatGen Param-1-2.9B-Instruct: the live Hugging Face metadata currently says Apache-2.0, while repository history contains a BharatGen Research License and the license file was subsequently changed/deleted. That history restricted use to non-commercial research and required written permission for public hosting. This unresolved, mutable license state blocks public deployment without written clarification. The two weight shards are about **5.72 GB**, excluding runtime overhead. The adapter pins revision `2024ac968cf289ba1cb6fde112a9abb437813b79` so `trust_remote_code=True` cannot silently fetch a later implementation. Private pretrained GPU model loading and 11 actual generations were subsequently verified on Colab T4 (2026-10-29).
- IndicTrans2: the correct distilled Hindi→English checkpoint is `ai4bharat/indictrans2-indic-en-dist-200M` (`hin_Deva` → `eng_Latn`), not the English→Indic variant. Its model page is MIT-labelled but gated and requires an authenticated user to accept contact-sharing terms. No repository credential is configured or required for the core MVP, so download/inference remain **unverified**.

## Rewrite quality protocol

`evaluation/rewrite_cases.csv` and `evaluation/evaluate_rewrites.py` define a
fixed 12-case genuine-inference and human-review workflow. Grammar and meaning
receive separate 1–5 judgements; target preservation and hallucinated additions
receive explicit binary checks. The summarizer rejects blank or out-of-range
judgements. No quality number exists until a real checkpoint run and completed
human review are committed as evidence.

## Test categories

- `tests/test_core.py` verifies transformations, input checks, formatting and error propagation using a fake model.
- `scripts/smoke_indicxlit.py` must execute the genuine pretrained model and assert a Devanagari result.
- Real results are committed under `evaluation/results/`; authentic Chromium screenshots and evidence are under `screenshots/`.

## Official sources

- https://github.com/AI4Bharat/IndicXlit
- https://github.com/AI4Bharat/IndicXlit/tree/master/app
- https://pypi.org/project/ai4bharat-transliteration/1.1.3/
- https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct
- https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct/commits/main
- https://github.com/AI4Bharat/IndicTrans2
- https://huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M


## Updated optional-model verification and licensing

The live BharatGen metadata says Apache-2.0, while repository history contains a restrictive BharatGen Research License and the license file has since changed. Public output/hosting remains blocked pending written clarification. The pinned BharatGen model was subsequently loaded and executed privately on T4; no public outputs or checkpoint service have been released.

A real test of MIT `manavdhamecha77/GEC-mT5-Small-Hindi` exposed severe script drift into Bengali, so it **failed quality review**. A second MIT checkpoint `Rucha-Ambaliya/mt5-small-indic-gec` ran on five Hindi sentences with two prompt variants and achieved 1/5 exact matches in either variant. Do not call either an effective grammar improvement module. The grammar UI is disabled by default.

Apache-2.0 `Qwen/Qwen2.5-0.5B-Instruct` was separately screened in run 40877372435. It exactly corrected 2/5 cases, but translated one response into English with changed meaning and made a severe noun substitution in another. It is not integrated and does not change the failed rewriting status.

Apache-2.0 `Qwen/Qwen3-0.6B` was screened in run 40878109536. It exactly corrected 0/5 cases and removed a meaning-bearing word from one output. It is not integrated.

Apache-2.0 `Helsinki-NLP/opus-mt-hi-en` **ran genuine Hindi-to-English inference successfully**, with two comprehensible examples (GitHub Actions run 40876423545). This is an independently attributed optional model, **not AI4Bharat IndicTrans2**. IndicTrans2 remains access-gated, with no executed inference.

Evidence: https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40876423545 and https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40876907788.


## Additional instruction-model screening

Independent Apache-2.0 Qwen2.5-0.5B-Instruct achieved 2/5 exact matches but committed major meaning changes; Qwen3-0.6B achieved 0/5 exact matches. Both were actually executed; neither is an Indian sovereign checkpoint or integrated as a trustworthy grammar feature. See actual CI logs under `.github/workflows/qwen-gec.yml` and `.github/workflows/qwen3-gec.yml`.


## Private BharatGen experimental milestone — 2026-10-29

**Genuine pretrained checkpoint inference VERIFIED on a user-authorized, private Colab Tesla T4.** Source evidence was received as an uncommitted ZIP, inspected for genuine model-load and generation events, and retained privately. Both official model-shard load and CUDA inference completed. Source commit `ef1cc3bd9457007f6adb15769630cfed97e82bc4`, immutable model revision `f9b32a727458727ff515fea5d82df00ae9b7ad56`, Python 3.12.16, Transformers 4.56.2, Torch 2.6.0+cu124, FP16. The 1-case smoke and all 10 registered Hindi cases passed nonempty, Hindi-script, EOS and truncation checks. Peak PyTorch GPU allocation was ~6.31 GiB. Mean generation latency over the ten cases was ~1.01 s per sentence.

A **preliminary non-expert editorial review** suggested nine of ten cases were acceptable or appropriately unchanged. One case failed technical-terminology fidelity and grammatical acceptability. This is not a broad benchmark or an independently scored human-linguist evaluation. Individual generated outputs and the raw ZIP remain private because the BharatGen Research License history conflicts with the model card's Apache-2.0 / MIT descriptions. Before publicly hosting weights or publishing generated outputs, obtain permission/clarification from BharatGen.

The Streamlit application now contains an explicitly gated, local-loopback-only **private research candidate** interface; it has not been validated in a full private GPU browser session. Public behavior remains genuine IndicXlit and independently attributed optional OPUS translation. It does **not** run BharatGen automatically on public users or claim production rewrite accuracy.
