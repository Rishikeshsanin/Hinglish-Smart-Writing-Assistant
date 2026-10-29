# Model implementation and evidence status

Last reviewed: 2026-10-29.

| Feature | Official checkpoint/package | Status |
| --- | --- | --- |
| Roman Hindi to Devanagari | AI4Bharat IndicXlit, `ai4bharat-transliteration==1.1.3` | Official API implemented; inference **NOT verified** as of initial commit |
| Hindi grammar rewriting | `bharatgenai/Param-1-2.9B-Instruct` | Not downloaded, not integrated, not executed |
| Hindi → English translation | AI4Bharat IndicTrans2 | Not downloaded, not integrated, not executed |

## Why genuine inference is still pending

The authoring environment cannot resolve external PyPI/Hugging Face hosts; Python packages and weights cannot be downloaded there. No fallback fake model is shipped. The optional GitHub Actions workflow named **Genuine IndicXlit model smoke (manual)** is supplied to test actual inference on an Ubuntu runner after triggering it manually. Mark as verified **only** once output and successful exit status have been inspected.

## Model considerations

- IndicXlit: ~11M transformer parameters, pretrained on Aksharantar, AI4Bharat repo MIT. Package release 1.1.3 uses legacy fairseq and may need a compatible Python/Linux stack; package metadata alone does not prove compatibility.
- BharatGen Param-1-2.9B-Instruct: Hugging Face lists Apache-2.0 metadata while its description mentions MIT, a discrepancy to resolve before broader use. Bilingual ~2.9B BF16 model with roughly **5.8 GB of raw weight tensors** (2 bytes * 2.9 billion), excluding KV caches, framework and tokenizer overhead. Early development checkpoint with the author's own alignment caveats. Laptop feasibility and model execution **unverified**.
- IndicTrans2: supports Hindi→English (`hin_Deva` to `eng_Latn`); official checkpoints MIT per project docs. Download/inference **unverified**.

## Test categories

- `tests/test_core.py` verifies transformations, input checks, formatting and error propagation using a fake model.
- `scripts/smoke_indicxlit.py` must execute the genuine pretrained model and assert a Devanagari result.
- Full evaluation results and real UI screenshots must follow successful inference; no results have been invented.

## Official sources

- https://github.com/AI4Bharat/IndicXlit
- https://github.com/AI4Bharat/IndicXlit/tree/master/app
- https://pypi.org/project/ai4bharat-transliteration/1.1.3/
- https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct
- https://github.com/AI4Bharat/IndicTrans2
