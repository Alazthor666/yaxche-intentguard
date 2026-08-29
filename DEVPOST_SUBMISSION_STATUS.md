# Devpost Submission Status — single source of truth

Last reconciled: 2026-08-28. This document separates code, observed runs, deployment, and independent verification.

| Submission item | Current evidence state | Claim allowed now? |
|---|---|---|
| Code repository | `https://github.com/Alazthor666/yaxche-intentguard` | Yes |
| Category | Collaborative Partner | Yes |
| Public judge demo | Firebase Hosting: `https://gen-lang-client-0554159756.web.app` | Yes |
| Deterministic intent boundary | Local suite: 45 passed; browser/Python parity: 22/22; GitHub CI `33231417270` passed for commit `0090bac` | Yes as `TESTED_REPORTED`; not independently verified |
| Collaborative feedback adaptation | Browser transforms `IntentPlan v1` to session-local `v2`; `external_actions = NONE` | Yes |
| Google ADK | Python implementation plus recorded ADK evidence path | Yes, state exact scope |
| Gemini 3.7 Flash in browser | Human observation was reported on 2026-08-28 in commit `8c4a12b`; no screenshot artifact is stored in this repository | Yes as `HUMAN_OBSERVED_REPORTED`, not independently verified |
| Firestore feedback | Protected rules and explicit separate save action; historical live gate is recorded | Yes with evidence caveat |
| Firebase Hosting | Public deployment and HTTP 200 were recorded | Yes |
| Cloud Run | Not deployed; billing-disabled path is not a claim | No |
| Independent verification / promotion | Not performed | No |

## Claim language

> YAXCHÉ IntentGuard is a Collaborative Partner that compiles a request into reviewable IntentIR before model reasoning. When a request could alter the recipient, scope, authorization, or reversibility of an action, it asks one precise question instead of guessing. A visible IntentPlan then adapts from explicit feedback in the same browser session, while declaring `external_actions = NONE`. Gemini 3.7 Flash, Google ADK, Firebase Hosting, and protected Firestore feedback are each described only to the extent supported by their evidence.

## Current rescue gate

```text
LOCAL_RESCUE_TESTS = 45_PASS + BROWSER_PARITY_22_22 + PLAN_CONTRACT_PASS
REMOTE_CI_FOR_MERGED_HEAD = SUCCESS  # GitHub Actions run 33231417270, commit 0090bac
PUBLIC_FIREBASE_DEPLOYMENT_FOR_MERGED_HEAD = PENDING
HUMAN_BROWSER_GEMINI = HUMAN_OBSERVED_REPORTED_2026-08-28
HUMAN_BROWSER_SCREENSHOT_ARTIFACT = NOT_IN_REPOSITORY
VIDEO_IN_ENGLISH_MAX_4_MIN = PREPARED_NOT_RECORDED
CLOUD_RUN_DEPLOYMENT = NOT_DEPLOYED
INDEPENDENT_VERIFICATION = false
```

`HUMAN_OBSERVED_REPORTED != INDEPENDENTLY_VERIFIED`. The capture procedure in [`docs/HUMAN_GEMINI_EVIDENCE_CAPTURE.md`](docs/HUMAN_GEMINI_EVIDENCE_CAPTURE.md) can create a reproducible artifact for the next observation. The video script is in [`docs/VIDEO_SCRIPT_EN.md`](docs/VIDEO_SCRIPT_EN.md).