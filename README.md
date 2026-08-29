# YAXCHÉ IntentGuard

> An adaptive collaborative AI agent that clarifies intent before taking action.

**Hackathon:** All Things Agentic Hackathon 2026
**Track:** The Collaborative Partner
**Project start:** 2026-08-26
**Public judge demo:** `DEPLOYED_ON_FIREBASE_HOSTING`
**Current local rescue candidate:** `REMOTE_CI_PENDING`
**Verification:** `TESTED_REPORTED != INDEPENDENTLY_VERIFIED`

YAXCHÉ IntentGuard is a new standalone hackathon project that turns ambiguous or messy human requests into structured, reviewable intent before an agent takes action. It is designed to ask the smallest useful clarification question when materially different interpretations would change the action, target, privacy boundary, or expected result.

## Why

Most AI systems optimize for answering quickly. IntentGuard optimizes for acting on the right intent.

The intended flow is:

```text
Human request
  -> clarification analysis
  -> minimum useful question when required
  -> structured IntentIR
  -> Gemini 3.7 Flash reasoning
  -> Google ADK orchestration
  -> bounded action / workflow
  -> persistent state + explicit feedback
  -> evidence for the next iteration
```

The hackathon requires Gemini 3.5 or newer. This project currently targets `gemini-3.7-flash`, aligning the battle implementation with the current Google Agents CLI examples while remaining above the competition model floor.

## Architecture

The repository is structured around five separable concerns:

1. **Clarification** — detect material ambiguity before execution.
2. **IntentIR** — normalize goals, constraints, unknowns and success criteria.
3. **Agent orchestration** — Google Agent Development Kit (ADK) with Gemini 3.7 Flash.
4. **State and feedback** — local deterministic storage for tests, with a Firestore adapter for the Google Cloud deployment path.
5. **Evidence** — reproducible tests and deployment evidence are kept distinct from claims.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/LIVE_VALIDATION.md`](docs/LIVE_VALIDATION.md), and [`PREEXISTING_WORK_DISCLOSURE.md`](PREEXISTING_WORK_DISCLOSURE.md).

## Evidence boundary

This README distinguishes implementation from execution:

```text
CODE_PRESENT != CLOUD_DEPLOYED
TEST_WRITTEN != TEST_EXECUTED
ADK_IMPORTED != END_TO_END_AGENT_PROVEN
MODEL_CONFIGURED != LIVE_MODEL_CALL_PROVEN
FIRESTORE_ADAPTER_PRESENT != FIRESTORE_DEPLOYMENT_PROVEN
CLOUD_RUN_CONFIG_PRESENT != CLOUD_RUN_DEPLOYMENT_PROVEN
```

The current evidence matrix lives in [`DEVPOST_SUBMISSION_STATUS.md`](DEVPOST_SUBMISSION_STATUS.md).

## Prerequisites

- Python 3.11+
- `uv` recommended (or a standard Python virtual environment)
- For real Gemini calls: a Gemini API key or supported Google Cloud credentials
- For Firestore: a Google Cloud project with Firestore enabled and Application Default Credentials
- For Cloud Run deployment: Google Cloud SDK and an authenticated project

## Reproducible local setup

### Option A — uv

```bash
git clone https://github.com/Alazthor666/yaxche-intentguard.git
cd yaxche-intentguard
cp .env.example .env
uv sync
```

Set `GEMINI_API_KEY` in `.env` for live model calls. Do not commit `.env`.

Run deterministic unit tests:

```bash
uv run pytest -q
```

Start the ADK development playground after credentials are configured:

```bash
uvx google-agents-cli playground
```

Run one live ADK prompt after credentials are configured:

```bash
uvx google-agents-cli run "I need to send the report. Help me do it."
```

The expected safe behavior is a focused clarification question rather than pretending the report was already sent. See [`docs/LIVE_VALIDATION.md`](docs/LIVE_VALIDATION.md) for the evidence gate.

### Option B — venv + pip

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -q
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

## Reproducible testing instructions

The minimum reproducible test gate is:

```bash
pytest -q
node tests/parity/browser_python_parity.mjs
```

Expected scope of this gate:

- IntentIR schema validation;
- deterministic ambiguity detection;
- minimum-clarification behavior;
- storage fallback behavior without cloud credentials.

Live-agent and cloud integration tests are deliberately separate because they require credentials and can incur usage. Their results must be recorded under `evidence/` before any submission claim says they passed.

## Environment variables

Copy `.env.example` to `.env` and configure only what you need.

- `GEMINI_API_KEY` — local Gemini API authentication.
- `GOOGLE_CLOUD_PROJECT` — target Google Cloud project for Firestore / deployment.
- `GOOGLE_CLOUD_LOCATION` — deployment location; default documented by this project is `us-central1`.
- `INTENTGUARD_STORAGE` — `memory` (default) or `firestore`.
- `INTENTGUARD_MODEL` — defaults to `gemini-3.7-flash`.

## Google stack: current truth

- **Gemini 3.7 Flash** (`gemini-3.7-flash`) through Firebase AI Logic in the public browser demo; a human browser observation is still required before claiming that this exact judge surface returned a live answer.
- **Google ADK** in the reproducible Python implementation and its separately recorded evidence path.
- **Firebase Hosting** for the public judge URL: <https://gen-lang-client-0554159756.web.app>.
- **Cloud Firestore** for explicitly saved feedback, protected by default-deny rules.
- **Cloud Run** remains an optional deployment path; it is not currently claimed as deployed.

The browser's local feedback adaptation does not call Gemini, Firestore, or any external action. It changes only a visible `IntentPlan` in the current session. See [`DEVPOST_SUBMISSION_STATUS.md`](DEVPOST_SUBMISSION_STATUS.md).

## Optional Cloud Run deployment path

`agents-cli-manifest.yaml` declares Cloud Run as the deployment target. Deployment is not considered complete until a real Cloud Run service and logs/evidence are captured.

Once Google Cloud credentials and project configuration are ready, the intended lifecycle is:

```bash
uvx google-agents-cli cmd-info --json
uvx google-agents-cli scaffold enhance --deployment-target cloud_run
uvx google-agents-cli deploy
```

Do not treat these instructions as proof that deployment already happened.

## Repository lineage and hackathon-new-work disclosure

IntentGuard was newly created for this hackathon on 2026-08-26. It is conceptually inspired by prior YAXCHÉ research, especially CADIPHI (human-intent compilation), but this repository begins as a new implementation. Any future reuse of pre-existing source code must be recorded with exact provenance in [`PREEXISTING_WORK_DISCLOSURE.md`](PREEXISTING_WORK_DISCLOSURE.md).

## Security

- Never commit API keys, service-account JSON, `.env`, tokens or credentials.
- Prefer Application Default Credentials for Google Cloud.
- The agent must distinguish understanding, proposal and authorization.
- A model recommendation is not an execution permit.

## License

No open-source license has been granted yet. Repository visibility does not by itself grant reuse rights.
