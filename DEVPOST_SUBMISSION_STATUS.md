# Devpost Submission Status

This file prevents draft-form fields from being confused with evidence-backed implementation claims.

| Devpost field | Current repository evidence | May claim now? |
|---|---|---|
| Code repo URL | Public repository exists | YES |
| Reproducible testing instructions in README | Present in `README.md` | YES |
| Google ADK used | Live runs exercise the ADK/Agents CLI surface; run `33076307241` passed the pre-model boundary gate | YES |
| Gemini 3.5+ used | Live run `33045663405` executed with `gemini-3.7-flash` | YES, live model path proven |
| Collaborative clarification behavior | Live run `33076307241` stopped material ambiguity before model reasoning | YES for the tested case |
| Cloud Run used | `agents-cli-manifest.yaml` targets Cloud Run | NOT YET; deployment evidence required |
| Firestore used | Firestore adapter and dependency are present | NOT YET; live Firestore evidence required |
| Hosted project URL | None yet | NO |
| Architecture diagram | Design artifact exists | YES as architecture design, not deployment proof |
| Reproducible tests passed | Live boundary run `33076307241` | YES: 15 passed |

## Current truth

```text
REPOSITORY_CREATED = true
REPRODUCIBLE_TEST_INSTRUCTIONS_PRESENT = true
DETERMINISTIC_TESTS_EXECUTED = true
DETERMINISTIC_TESTS_PASS = true
DETERMINISTIC_TEST_COUNT = 15
ADK_IMPORT_AND_CONSTRUCTION_PROVEN = true
ADK_LIVE_AGENT_PATH_PROVEN = true
ADK_TOOL_CALL_PROVEN = true                 # separately observed in run 33045663405
GEMINI_MODEL_ID_CONFIGURED = gemini-3.7-flash
GEMINI_LIVE_CALL_PROVEN = true             # run 33045663405
PRE_MODEL_INTENT_BOUNDARY_IMPLEMENTED = true
PRE_MODEL_INTENT_BOUNDARY_LIVE_PROVEN = true # run 33076307241
CORE_CLARIFICATION_TESTED_CASE = PASS
FIRESTORE_ADAPTER_PRESENT = true
FIRESTORE_LIVE_USE_PROVEN = false
CLOUD_RUN_TARGET_CONFIGURED = true
CLOUD_RUN_DEPLOYMENT_PROVEN = false
HOSTED_URL_AVAILABLE = false
VERIFIED = false
PROMOTED = false
```

Evidence:

- deterministic baseline: [`evidence/CI_RUN_33043470358.md`](evidence/CI_RUN_33043470358.md)
- first live infrastructure failure: [`evidence/LIVE_GEMINI_GATE_RUN_33045200154_FAILURE.md`](evidence/LIVE_GEMINI_GATE_RUN_33045200154_FAILURE.md)
- first successful live Gemini/ADK path with behavioral finding: [`evidence/LIVE_GEMINI_GATE_RUN_33045663405.md`](evidence/LIVE_GEMINI_GATE_RUN_33045663405.md)
- clarification repair CI: [`evidence/CI_RUN_33046202716.md`](evidence/CI_RUN_33046202716.md)
- model-tool-selection enforcement failure: [`evidence/LIVE_GEMINI_GATE_RUN_33046624824_BEHAVIORAL_ENFORCEMENT_FAILURE.md`](evidence/LIVE_GEMINI_GATE_RUN_33046624824_BEHAVIORAL_ENFORCEMENT_FAILURE.md)
- successful deterministic pre-model live boundary: [`evidence/LIVE_INTENT_BOUNDARY_RUN_33076307241.md`](evidence/LIVE_INTENT_BOUNDARY_RUN_33076307241.md)
- live validation procedure: [`docs/LIVE_VALIDATION.md`](docs/LIVE_VALIDATION.md)

The live Gemini model path and the deterministic pre-model intent boundary are both proven, by separate runs with separate claims. Firestore and Cloud Run remain unproven until live cloud evidence exists.
