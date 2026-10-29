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

## Executed evidence and quality gate

The actual optional-model smoke workflow is [here](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/workflows/language-model-smoke.yml). **Do not claim verified until its inference logs pass**; stubbed tests of adapter wiring never count as model execution. Qualitative output review is separate from automatic text metrics.

Real-model run [40876762493](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40876762493) executed both checkpoints on CPU. The Hindi GEC checkpoint failed the quality gate: its three outputs were Bengali or mixed Bengali/Hindi and did not preserve the source meaning. The script-level safeguard now rejects such output, and the UI grammar button remains behind the separate `INDICWRITE_ENABLE_GEC_EXPERIMENTAL=1` research flag.

The same run produced `I have to go to college tomorrow.` and `Hello, how are you?` for two Hindi inputs. These are plausible meaning-preserving OPUS-MT smoke outputs, but two examples are not a translation benchmark.

Full browser run [40879090261](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40879090261) then passed the real user journey from Roman Hindi through IndicXlit and OPUS-MT. It observed `Tomorrow I go to college!`, verified the research grammar control was disabled, cleared the UI, and uploaded a screenshot artifact. This proves integration of that one flow, not general translation accuracy.

A second MIT candidate, `Rucha-Ambaliya/mt5-small-indic-gec`, was executed in run [40876907788](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40876907788). It exactly corrected only the duplicated-word case (**1/5**) and returned the erroneous source unchanged for the other four cases. Adding `correct this: ` made no difference. This candidate is therefore not integrated.

A third, explicitly non-sovereign Apache-2.0 candidate, `Qwen/Qwen2.5-0.5B-Instruct`, was executed in run [40877372435](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40877372435). It exactly corrected **2/5** cases, left one error unchanged, translated one Hindi case into English with changed meaning, and replaced “books” with “features” in another. It also fails the quality gate and is not integrated.

`Qwen/Qwen3-0.6B` was executed separately in run [40878109536](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40878109536). It produced **0/5** exact corrections, copied four erroneous inputs substantially unchanged, and removed the word “food” from the duplicated-word case. It also fails the quality gate and is not integrated.

## Rewriting assessment (human judgment)

The five-case candidate comparisons above are screening results, not complete human evaluations. Before any Hindi rewriter is enabled by default, rate ten or more genuine pairs on (1) grammaticality, (2) meaning preservation, (3) entity/number integrity, and (4) useful vs unnecessary edits. Do not claim broader quality from exact match on five examples.
