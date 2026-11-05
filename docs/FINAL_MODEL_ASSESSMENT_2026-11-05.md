# Final optional-model assessment — 5 November 2026

## Release decision

The supported public conversion release is complete. The original broader
writing vision remains approximately **90% complete (engineering estimate,
not a measured acceptance percentage)**. Automatic grammar, public rewriting,
and publicly enabled translation do not meet all acceptance gates. No new
model is enabled on production by this assessment.

## New authentic OPUS-MT evidence

PR #44 merged at `63cae3cf4e81ab2c19b904d57d98ddbe81b07478` adds a manually
dispatched, isolated CPU evaluation and runtime metadata. Real run
[42080432443](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/42080432443)
generated **12/12** fixed cases with `Helsinki-NLP/opus-mt-hi-en`, checkpoint
`a7d96a16729f812578bd55e7366147beda625d86`, Python 3.12.16 and
Transformers 4.56.2. Loading: **10.879 s**; total generation: **3768.46 ms**.
The original evaluator, cases, and private-output safeguards are retained.

A separate Windows/Python 3.12.10 real run used the same checkpoint and
completed 12/12; loading took 47.486 s and generation 7673.73 ms. Outputs
and blank human-review sheets remain in ignored `private_research/`.

Assistant qualitative inspection (not independent bilingual human scoring):

- T03 changes evening to morning, a material time error.
- T10 corrupts the English meeting term.
- T11 omits the denominator 18 and changes participation to fleeing.
- The other nine cases have no obvious essential-meaning error in this small
  assistant review; T02 and T12 still have awkward English grammar.

The automatic warning IDs were T03, T10, T11 in both runs. These string
checks are alerts, not semantic scores. Human adequacy/fluency fields remain
unfilled; no invented human ratings or broad accuracy claim is made.
**Public integration is rejected on quality grounds.** A free runner proving
CPU execution does not establish reliable shared Streamlit memory, latency,
or uptime. Existing optional local translation remains explicitly experimental.

## Grammar correction

Existing genuine trials already reject GEC-mT5-Small-Hindi (script/meaning
drift), mt5-small-indic-gec (1/5 exact correction), Qwen2.5-0.5B (2/5 and
semantic errors), and Qwen3-0.6B (0/5). See OPTIONAL_MODELS.md for original
run links. Automatic correction stays disabled; manual editing remains.
No additional model quality or inference is claimed for this assessment.

## BharatGen

Repository evidence records one smoke plus ten private pinned T4 generations,
approximately 6.31 GiB peak allocated GPU memory, and preliminary assistant
review; independent human quality review and real GPU/browser QA remain
incomplete. The private evidence ZIP was not found in the inspected local
project/Documents/Downloads locations, so it was not newly reviewed.

The current model card is Apache-2.0 labeled, but `main/LICENSE` returned 404.
The historical LICENSE at revision
`13498f81c10fba9d716ea2969d00df3538c10ca7` remains accessible and requires
written permission for public output distribution and hosting, including free
services. Metadata conflicts do not resolve permission for existing private
outputs. Public rewriting stays disabled pending written clarification and
quality/resource acceptance. No restricted outputs or weights are published.

Sources: [current card](https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct),
[historical license](https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct/blob/13498f81c10fba9d716ea2969d00df3538c10ca7/LICENSE).

## IndicTrans2

The [official 200M checkpoint](https://huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M)
still requires the account holder to accept sharing account information and
model access conditions. Its card is MIT labeled. No authorized checkpoint
access was established in this session; no gated files, weights or remote
code were downloaded. It remains disabled with issue #3 open.

## Fresh production and regression evidence

- [Public Streamlit run 42079900448](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/42079900448):
  PASS; ten distinct genuine conversions, mixed-language preservation,
  editing, clipboard, downloads, validation, clear-state and keyboard checks;
  no horizontal overflow at 320/390/768/1440. Evidence artifacts include
  screenshots and browser-evidence.json. Verified baseline SHA:
  `7459a3a36caccd421bf62850d1611d1c8951c584`.
- [Public Vercel run 42079907938](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/42079907938):
  PASS; existing gateway and native-converter link tested in Chromium.
- [Post-merge unit run 42080430121](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/42080430121):
  **154 passed, 8 skipped**. Optional skipped model tests are not inference.
- Local Windows with unrelated globally installed optional dependencies:
  **159 passed, 4 failed**. Failures concern Windows text decoding, unavailable
  POSIX fcntl, a Transformers version differing from the research pin, and
  Git CRLF checkout versus a byte-exact LF fixture. This is not represented
  as a passing supported Linux release suite.
- Original IndicXlit 40-case predictions/metrics unchanged: CER 5.58%, word
  accuracy 82.67%, exact match 22/40. No replacement model or new benchmark.

Production URLs remain:
- https://hinglish-smart-writing-assistant-indicwrite-rishi.streamlit.app/
- https://indicwrite-public-web.vercel.app/

## Remaining external gates

1. A translation model with acceptable meaning preservation, followed by
   bilingual review and public-host resource qualification.
2. A grammar model that passes quality screening.
3. BharatGen licensing clarification, available private evidence and independent
   reviewer/GPU UI checks; no free reliable public GPU endpoint established.
4. Account-holder acceptance of IndicTrans2 access, reviewed/pinned custom code,
   genuine inference and comparison.

Issues #1, #2 and #3 remain open because their full acceptance criteria are
not fulfilled. The verdict is **supported public converter verified; optional
writing vision incomplete for documented quality/access/license reasons**.
