# Live Gemini Gate — Failure Receipt

Run: `33045200154`
Workflow: `live-gemini-gate`
Commit under test: `a9134d37ce142fff1dac558df3101d4177aafc99`
Result: `FAILURE`

## What passed

- GitHub Secret `GEMINI_API_KEY` was present; its value was not printed.
- Dependency installation completed.
- Deterministic gate completed with `10 passed`.

## What failed

The live ADK/Gemini step did not reach a model call. `agents-cli v1.4.1` exited because `uv` was not installed or on `PATH`.

Observed boundary:

```text
SECRET_PRESENT = true
DETERMINISTIC_TESTS_PASS = true
LIVE_MODEL_CALL_ATTEMPT_REACHED = false
GEMINI_LIVE_CALL_PROVEN = false
```

## Corrective action

Workflow `.github/workflows/live_gemini_gate.yml` was amended to install `uv` explicitly before invoking `agents-cli`.
Corrective commit: `7e3bdb94c43d44eeed57e383b106e6c6eb33784c`.

This failure is retained as evidence and is not counted as a Gemini runtime pass.
