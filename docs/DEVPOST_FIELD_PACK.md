# Devpost Field Pack — YAXCHÉ IntentGuard

Recheck `DEVPOST_SUBMISSION_STATUS.md` immediately before submitting.

## Stable fields

- **Submitter type:** Individuals
- **Country of residence:** Mexico
- **Category:** Collaborative Partner
- **Project start date:** 08-26-26
- **Repository:** `https://github.com/Alazthor666/yaxche-intentguard`
- **Hosted project URL:** `https://gen-lang-client-0554159756.web.app`
- **Google SDK / framework:** Agent Development Kit (ADK)
- **Google AI model:** Gemini 3.7 Flash
- **Google Cloud / Firebase services:** Firebase Hosting, Firebase AI Logic, Cloud Firestore; Cloud Run is an optional non-deployed path and must not be claimed as live.

## Judge testing instructions

```text
Open https://gen-lang-client-0554159756.web.app.

1. Click “Ambiguous send” and Analyze intent. The page must pause before Gemini and ask who should receive it / whether execution is authorized.
2. Click “Clear bounded task” and Analyze intent. A human Gemini response was reported on 2026-08-28; capture a new runtime badge and response if you reproduce it, without bypassing App Check.
3. Enter: “Ask one precise question at a time.” Click “Apply feedback to plan (local only)”. The visible IntentPlan changes from v1 to v2 and continues to state external_actions = NONE and persistence = SESSION_LOCAL_ONLY.
4. “Save feedback separately” is deliberately a second, protected Firestore action. It is not required to demonstrate the safe local adaptation.

For local reproducibility: Python 3.11+, `pip install -e ".[dev]"`, `pytest -q`, and `node tests/parity/browser_python_parity.mjs`.
```

## Submission checklist

- [ ] Record the English video (under four minutes).
- [ ] Attach a screenshot/note for the reported human Gemini browser observation if the submission will rely on it.
- [ ] Upload the architecture diagram and screenshots.
- [ ] Confirm the remote CI result for the exact submitted commit.
- [ ] Keep Cloud Run and independent verification unchecked unless new evidence exists.