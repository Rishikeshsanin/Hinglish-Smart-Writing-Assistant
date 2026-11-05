# IndicWrite collaboration and fast-track handoffs

This is an **individual CS3235 project**, with independent AI-assisted
development/review tracks. The student must understand and truthfully report
the code and experimental evidence.

## Single repository boundary

`Rishikeshsanin/Hinglish-Smart-Writing-Assistant` only. Never modify, deploy,
query databases for, or share credentials from DeckVerse, ReturnReview,
Supabase hubs, or any other user projects. No agent should merge without
coordinator review. Never commit tokens, checkpoints or downloaded data.

## Coordinator (connected GitHub account)
Track [issue #1](../issues/1) and all CI runs; own source integration,
verification, release decisions, and accurate progress disclosures. Only
merge/push changes with evidence. Report commit SHA and tests per milestone.

## Independent reviewer on friend's unconnected ChatGPT account

The public repository can be read in normal ChatGPT chat or a browser in Work
mode, but this **does not grant GitHub write access** or connect the user's
accounts. Do not provide login credentials or personal tokens. Deliver
a review and optional patch suggestions in text; coordinator implements them.

- Faculty-rubric gap audit: what is genuinely complete versus not executed.
- Check recorded outputs in `evaluation/results/predictions.csv` against
  `evaluation/cases.csv` and the report; flag unsupported claims.
- Draft 10+ paired Hindi rewriting evaluation cases and a human meaning-
  preservation scoring rubric; don't pretend outputs from an unrun model.
- Check README Windows/WSL2 setup, screenshots, accessibility and copy.

## Dedicated workstreams

1. [#2 BharatGen model](../issues/2): optional experimental adapter and
   genuine inference smoke first. Current adapter is **NOT EXECUTED**.
2. [#3 IndicTrans2](../issues/3): only after access/license agreement; optional.
3. [#4 Safe deployment](../issues/4): isolated dedicated service and verified
   real conversion; never repurpose another app's hosting.

## Release gate

Transliteration is **verified**. Real BharatGen rewriting and IndicTrans2
translation **must remain unverified** until logged pretrained inference and
human-evaluated outputs exist. Automated prompt-shape tests are not model
evaluation. Public deployment must show a reachable independently tested URL.

## Progress reporting format

- Workstream / status: completed, blocked, or in progress
- Changed files, branch, exact Git SHA / issue / PR link
- Tests actually executed and real model(s) actually run
- Any failures or compliance gaps
- Approximate MVP and full-scope completion separately, labeled estimates
- Next specific action

Do not assume two independent ChatGPT chats communicate automatically: paste
handoffs or commit them to GitHub for coordinator review.


## Current verified handoff (5 November 2026; supersedes early project snapshot)

Agents A/B/C have been integrated via PRs #37/#38/#40; the optional-model
runtime fix is PR #41. The independent ten-case product QA PR #42 merged at
`3567aa1b9f36b91db0030626856d0b3f6d769606`. Its [post-merge external
Chromium CI run 42073053397](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/42073053397)
passed 10 genuine official-IndicXlit public cases plus a mixed-language case,
real clipboard and Unicode downloads, keyboard controls and four viewports.
This documents the **core conversion product** only; no inference was mocked.

Later private research evidence confirms BharatGen pinned-pretrained T4
inference (1 smoke + 10 cases), but NOT human-certified semantic/grammar
quality and NOT permission to publish generated results or host the model.
IndicTrans2 remains access-gated; experimental grammar correction remains
disabled. Never leak private research data. A free-host public browser success
is not a guarantee of uptime or complete WCAG accessibility.
