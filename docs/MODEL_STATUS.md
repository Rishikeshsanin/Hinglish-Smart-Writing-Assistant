# Model implementation and evidence status

Last reviewed: 2026-10-29. Real-model and browser evidence verified.

| Feature | Official checkpoint/package | Status |
| --- | --- | --- |
| Roman Hindi to Devanagari | AI4Bharat IndicXlit, `ai4bharat-transliteration==1.1.3` | Official neural inference **VERIFIED** on GitHub Actions (run 40870311669) |
| Hindi grammar rewriting | `bharatgenai/Param-1-2.9B-Instruct` | Not downloaded, not integrated, not executed |
| Hindi → English translation | AI4Bharat IndicTrans2 | Not downloaded, not integrated, not executed |

## Why genuine inference is still pending

The initial runner installed the package and downloaded the 121 MB checkpoint but failed due to PyTorch 2.6+ restricted legacy Fairseq checkpoint loading. Scoped allowlisting of the official checkpoint's `argparse.Namespace` resolved this. Follow-up GitHub Actions run **40870311669** passed real inference on three sample sentences; run **40870722731** executed forty genuine predictions; run **40871267464** passed Chromium desktop/mobile UI checks. No mock results were used for these executed checks.

## Model considerations

- IndicXlit: ~11M transformer parameters, pretrained on Aksharantar, AI4Bharat repo MIT. Package release 1.1.3 uses legacy fairseq and may need a compatible Python/Linux stack; package metadata alone does not prove compatibility.
- BharatGen Param-1-2.9B-Instruct: Hugging Face lists Apache-2.0 metadata while its description mentions MIT, a discrepancy to resolve before broader use. Bilingual ~2.9B BF16 model with roughly **5.8 GB of raw weight tensors** (2 bytes * 2.9 billion), excluding KV caches, framework and tokenizer overhead. Early development checkpoint with the author's own alignment caveats. Laptop feasibility and model execution **unverified**.
- IndicTrans2: supports Hindi→English (`hin_Deva` to `eng_Latn`); official checkpoints MIT per project docs. Download/inference **unverified**.

## Test categories

- `tests/test_core.py` verifies transformations, input checks, formatting and error propagation using a fake model.
- `scripts/smoke_indicxlit.py` must execute the genuine pretrained model and assert a Devanagari result.
- Real results are committed under `evaluation/results/`; authentic Chromium screenshots and evidence are under `screenshots/`.

## Official sources

- https://github.com/AI4Bharat/IndicXlit
- https://github.com/AI4Bharat/IndicXlit/tree/master/app
- https://pypi.org/project/ai4bharat-transliteration/1.1.3/
- https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct
- https://github.com/AI4Bharat/IndicTrans2


## Updated optional-model verification and licensing

Actual BharatGen checkpoint license is **BharatGen Research License**, despite an Apache-2.0 badge in metadata. Its terms require written permission to publicly share outputs or deploy its weights. No BharatGen inference is verified; a local research notebook exists.

A real test of MIT `manavdhamecha77/GEC-mT5-Small-Hindi` exposed severe script drift into Bengali, so it **failed quality review**. A second MIT checkpoint `Rucha-Ambaliya/mt5-small-indic-gec` ran on five Hindi sentences with two prompt variants and achieved 1/5 exact matches in either variant. Do not call either an effective grammar improvement module. The grammar UI is disabled by default.

Apache-2.0 `Helsinki-NLP/opus-mt-hi-en` **ran genuine Hindi-to-English inference successfully**, with two comprehensible examples (GitHub Actions run 40876423545). This is an independently attributed optional model, **not AI4Bharat IndicTrans2**. IndicTrans2 remains access-gated, with no executed inference.

Evidence: https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40876423545 and https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40876907788.


## Additional instruction-model screening

Independent Apache-2.0 Qwen2.5-0.5B-Instruct achieved 2/5 exact matches but committed major meaning changes; Qwen3-0.6B achieved 0/5 exact matches. Both were actually executed; neither is an Indian sovereign checkpoint or integrated as a trustworthy grammar feature. See actual CI logs under `.github/workflows/qwen-gec.yml` and `.github/workflows/qwen3-gec.yml`.
