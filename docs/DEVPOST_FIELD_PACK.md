# Devpost Field Pack — YAXCHÉ IntentGuard

Use this as the current draft-form source. Recheck `DEVPOST_SUBMISSION_STATUS.md` before final submission.

## Stable fields

**Submitter Type**  
`Individuals`

**Country of residence**  
`Mexico`

**Category**  
`Collaborative Partner`

**Organization name**  
Leave blank — this submission is not on behalf of an organization.

**Project start date**  
`08-26-26`

**Code repository URL**  
`https://github.com/Alazthor666/yaxche-intentguard`

**Reproducible Testing instructions in README?**  
`Yes`

**Google SDK**  
`Agent Development Kit (ADK)`

Rationale: the repository imports and constructs a real Google ADK Agent/App and CI run `33043470358` passed the import check.

## Cloud/model fields — draft target, final evidence gate required

**Google Cloud services planned/integrated**  
`Cloud Run` + `Firestore`

Current truth: Cloud Run deployment target and Firestore adapter exist, but real deployed-service / live Firestore evidence is still pending. They must not remain final claims if the evidence gate is not completed.

**Google AI model**  
`Gemini 3.5 Flash`

Current truth: `gemini-3.5-flash` is configured in the ADK agent and accepted at construction; a live Gemini inference receipt is still pending.

**Hosted project URL**  
Leave blank until Cloud Run deployment creates a real URL.

## Testing instructions for judges

Paste this into the optional testing-instructions field if desired:

```text
Clone https://github.com/Alazthor666/yaxche-intentguard and use Python 3.11+.

1. python -m venv .venv
2. Activate the virtual environment.
3. pip install -e ".[dev]"
4. pytest -q tests/unit

The deterministic suite requires no cloud credentials. A green reference execution is GitHub Actions run 33043470358: 10 tests passed and the Google ADK app/root agent imported successfully.

Live Gemini, Firestore, and Cloud Run integration require Google credentials and are tracked separately from deterministic tests. See README.md and DEVPOST_SUBMISSION_STATUS.md for the current evidence boundary.
```

## Startup Excellence

Do not opt in under the current individual submission. Leave incorporated-organization name and corporate email blank.

## Architecture diagram

Upload the PNG architecture artifact prepared for the hackathon. Its presence documents the intended architecture; deployment proof remains separate.

## Final-submission stop conditions

Do not submit final until all mandatory competition claims are true and evidenced:

```text
LIVE_GEMINI_CALL_PROVEN = true
CLOUD_RUN_DEPLOYMENT_PROVEN = true
FIRESTORE_LIVE_USE_PROVEN = true
ARCHITECTURE_DIAGRAM_UPLOADED = true
DEMO_VIDEO_READY = true
PUBLIC_OR_JUDGE_ACCESS_REPO_READY = true
README_REPRODUCIBLE = true
```
