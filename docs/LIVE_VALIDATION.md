# Live Validation Gate

This gate converts configuration-level claims into live evidence without committing credentials.

## Preconditions

- Python 3.11+
- project dependencies installed
- a local `.env` containing `GEMINI_API_KEY` (never commit `.env`)
- `INTENTGUARD_MODEL=gemini-3.7-flash`

## Gate L1 — live ADK + Gemini response

From the repository root:

```bash
uvx google-agents-cli run "I need to send the report. Help me do it."
```

Expected behavior:

1. the request reaches the ADK agent;
2. Gemini performs a real inference;
3. IntentGuard invokes or follows the intent-compilation behavior;
4. the response does not claim an external action occurred;
5. if the request is materially ambiguous, the agent asks a focused clarification question.

Record the terminal output, timestamp, model identifier and commit SHA under `evidence/`. Never record the API key.

## Gate L2 — local persistent feedback path

Keep a session alive and provide explicit feedback. Verify the agent invokes the feedback tool. Local memory evidence is useful for behavior debugging but does not prove Firestore.

## Gate L3 — Firestore

Set:

```text
INTENTGUARD_STORAGE=firestore
GOOGLE_CLOUD_PROJECT=<project-id>
```

Use Application Default Credentials and execute a feedback interaction. Verify a document appears in the `intentguard_feedback` collection and capture non-secret evidence.

## Gate L4 — Cloud Run

After the project has valid Google Cloud credentials and billing/credits:

```bash
uvx google-agents-cli scaffold enhance --deployment-target cloud_run
uvx google-agents-cli deploy
```

Capture the Cloud Run service URL, deployment timestamp, revision, logs and the exact tested commit. A deployment config file alone is not deployment proof.

## Evidence boundary

```text
ADK_IMPORT_PASS != LIVE_GEMINI_PASS
LIVE_GEMINI_PASS != FIRESTORE_PASS
FIRESTORE_PASS != CLOUD_RUN_PASS
CLOUD_RUN_PASS != DEVPOST_FINAL_READY
```
