# Devpost Submission Status — single source of truth

Last reconciled: 2026-08-28. This document distinguishes a deployed public page from a human-proven live model response.

| Submission item | Evidence-backed status | Claim allowed now? |
|---|---|---|
| Code repository | `https://github.com/Alazthor666/yaxche-intentguard` | Yes |
| Category | Collaborative Partner | Yes |
| Public judge demo | Firebase Hosting: `https://gen-lang-client-0554159756.web.app` | Yes |
| Deterministic intent boundary | Local suite: `39 passed`; browser/Python parity: `22/22` | Yes, label `TESTED_REPORTED` until remote CI completes |
| Feedback adapts collaboration | Browser creates `IntentPlan v1`, then feedback creates session-local `v2`; external actions = `NONE` | Yes |
| Google ADK | Present in the Python implementation; prior evidence is recorded separately | Yes, describe exact scope |
| Gemini 3.7 Flash in browser | Firebase AI Logic configured | Partial: human browser proof still required |
| Firestore feedback | Rules and explicit save path exist; historical live gate is recorded | Yes only with the evidence caveat |
| Firebase Hosting | Public HTTP 200 deployment recorded | Yes |
| Cloud Run | Not deployed; billing-disabled path is not a submission claim | No |
| Independent verification / promotion | Not performed | No |

## Exact claim language

Use this description in the Devpost draft:

> YAXCHÉ IntentGuard is a Collaborative Partner that compiles a request into reviewable IntentIR before any model reasoning. If the request could change the recipient, scope, authorization, or reversibility of an action, it asks one precise question instead of guessing. Judges can then apply feedback to a visible session-local IntentPlan. That feedback changes collaboration behavior without sending, deleting, publishing, or saving anything automatically. Gemini 3.7 Flash, Google ADK, Firebase Hosting, and protected Firestore feedback provide the Google stack; each integration is labeled according to its evidence.

## Required final evidence still missing

```text
REMOTE_CI_FOR_CURRENT_HEAD = PENDING
HUMAN_BROWSER_GEMINI_RESPONSE = PENDING
VIDEO_IN_ENGLISH_MAX_4_MIN = PREPARED_NOT_RECORDED
DEVPOST_SCREENSHOTS_AND_ARCHITECTURE_UPLOAD = PENDING
```

Do not convert any `PENDING` item into a green claim. The human Gemini procedure is in [`docs/HUMAN_GEMINI_EVIDENCE_CAPTURE.md`](docs/HUMAN_GEMINI_EVIDENCE_CAPTURE.md); the recording script is in [`docs/VIDEO_SCRIPT_EN.md`](docs/VIDEO_SCRIPT_EN.md).