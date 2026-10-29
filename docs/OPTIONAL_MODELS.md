# Optional model-based writing and translation (independent track)

**Last updated:** 2026-10-29. The core AI4Bharat IndicXlit path remains independent.

## Why not silently substitute BharatGen?

The actual [BharatGen Research License](https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct/blob/main/LICENSE) permits academic work but says **written approval is required to publicly publish model outputs or host the checkpoint**. Its HF model metadata says Apache-2.0 while the actual license text imposes restrictions. We follow the restrictive license text until clarified. No public BharatGen model/outputs are included in this repository. Experimental local notebook remains available without proof of inference.

## Genuine alternative Hindi grammar model

[manavdhamecha77/GEC-mT5-Small-Hindi](https://huggingface.co/manavdhamecha77/GEC-mT5-Small-Hindi) is a **separate MIT-licensed mT5-small Hindi grammatical error correction model**, trained for noisy-to-clean Hindi sentence correction. It is **not** a BharatGen checkpoint and is not advertised as such. The model card documents a literal `correct this: ` prefix and a 128-token input limit.

## Optional English translation

[Helsinki-NLP/opus-mt-hi-en](https://huggingface.co/Helsinki-NLP/opus-mt-hi-en) is Apache-2.0, Hindi-to-English. It is **not** AI4Bharat IndicTrans2; the latter's distilled model requires accepting Hugging Face conditions in a user's own account. No HF credentials are committed.

## Install and run (CPU and locally)

On the verified Linux / Python 3.10 base:

```bash
python -m pip install -r requirements-language-services.txt
INDICWRITE_ENABLE_LANGUAGE_SERVICES=1 PYTHONPATH=src streamlit run app.py
```

Check actual checkpoints separately:

```bash
PYTHONPATH=src python scripts/smoke_language_models.py
```

The optional checkpoints can be hundreds of MB or more and are lazily downloaded on first use. The model may produce semantically wrong or awkward rewrites; users must compare original and output. No saved personal text/history and no model results are faked. Translation and rewrite are independent: either one failing must not break IndicXlit.

## Evidence gate

The actual optional-model smoke workflow is [here](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/workflows/language-model-smoke.yml). **Do not claim verified until its inference logs pass**; stubbed tests of adapter wiring never count as model execution. Qualitative output review is separate from automatic text metrics.

## Rewriting assessment (human judgment)

Rate ten or more pairs on (1) grammaticality, (2) meaning preservation, (3) entity/number integrity, and (4) useful vs unnecessary edits. Use scale 0 (fails), 1 (mixed) and 2 (good). Do not claim quantitative human ratings until evaluated by a reviewer; report actual examples with checkpoint names.
