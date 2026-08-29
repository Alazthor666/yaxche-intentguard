# YAXCHÉ IntentGuard

> An adaptive collaborative AI agent that clarifies intent before taking action.

**Hackathon:** All Things Agentic Hackathon 2026  
**Track:** The Collaborative Partner  
**Project start:** 2026-08-26  
**Status:** `IMPLEMENTATION_STARTED_NOT_YET_DEPLOYED`  
**Verification:** `NOT_YET_EXTERNALLY_VERIFIED`

YAXCHÉ IntentGuard is a new standalone hackathon project that turns ambiguous or messy human requests into structured, reviewable intent before an agent takes action. It is designed to ask the smallest useful clarification question when materially different interpretations would change the action, target, privacy boundary, or expected result.

**Live demo:** https://gen-lang-client-0554159756.web.app — the boundary self-test runs in your own browser on page load.

## Why

Most AI systems optimize for answering quickly. IntentGuard optimizes for acting on the right intent.

The failure mode that will actually hurt people as agents gain authority is not hallucination. It is confident action on a misread instruction: the right verb aimed at the wrong target, the wrong recipient, or a scope nobody authorized.

## The part that is not a prompt

Almost every attempt to make an agent cautious is written as an instruction — *ask before you act, do not assume the recipient*. An instruction is a request to a probabilistic system. It holds most of the time, which is another way of saying it fails some of the time, and it fails exactly when the request is unusual enough to matter.

IntentGuard's boundary is an ADK `before_model_callback`. The framework runs it before the model is invoked at all, so a materially ambiguous request never reaches Gemini regardless of what the model would have preferred to do with it.

```text
INSTRUCTION_IS_A_REQUEST
CALLBACK_IS_A_BOUNDARY
PROMPT_COMPLIANCE != ENFORCEMENT
```

It installs on any ADK agent in three lines:

```python
from google.adk.agents import Agent
from app.guardrail import install_intent_boundary

agent = Agent(name="my_agent", model=..., instruction=...)
install_intent_boundary(agent)
```

`install_intent_boundary` refuses to overwrite a callback that is already there. Silently replacing another team's safety hook would be the same class of mistake this project exists to prevent.

## Measured in both directions

Every safety demo shows a system blocking something. Almost none report how often it blocks work that was fine — which is the number that decides whether anyone leaves it switched on.

```text
CATCH_RATE      100%   19/19 materially ambiguous requests stopped
FALSE_STOP_RATE   0%    0/12 clear requests interrupted
```

Reproduce with `python scripts/run_boundary_benchmark.py`. The corpus is hand-built and small, it is stated as such in the output, and both rates run in CI so neither can drift unnoticed.

Five classes fire, ordered so the most consequential one asks the question: **money** (value moves without an exact amount and payee), **irreversible** (a dangling pronoun is not a target), **scope** (an unbounded quantifier changes blast radius), **access** (naming who, never what they may do), **outward** (anything leaving the agent needs a known recipient).

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
pytest -q tests/unit
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

## Google stack target

The hackathon implementation is being built around:

- Gemini 3.7 Flash (`gemini-3.7-flash`; competition floor is Gemini 3.5+)
- Google Agent Development Kit (ADK)
- Google Cloud Run
- Cloud Firestore

The repository may contain integration code/configuration for a service before deployment evidence exists. See the evidence boundary above.

## Cloud deployment path

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
