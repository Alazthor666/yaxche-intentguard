# Devpost Submission Status

This file prevents draft-form fields from being confused with evidence-backed implementation claims.

| Devpost field | Current repository evidence | May claim now? |
|---|---|---|
| Code repo URL | Public repository exists | YES |
| Reproducible testing instructions in README | Present in `README.md` | YES |
| Google ADK used | Live run `33045663405` started the agent and produced a real ADK tool call | YES |
| Gemini 3.5+ used | Live run `33045663405` executed with `gemini-3.7-flash` | YES, live model path proven |
| Cloud Run used | `agents-cli-manifest.yaml` targets Cloud Run | NOT YET; deployment evidence required |
| Firestore used | Firestore adapter and dependency are present | NOT YET; live Firestore evidence required |
| Hosted project URL | None yet | NO |
| Architecture diagram | Design artifact exists | YES as architecture design, not deployment proof |
| Reproducible tests passed | Live run `33045663405` | YES: 10 passed on that tested commit; newer repair CI pending/currently separate |

## Current truth

```text
REPOSITORY_CREATED = true
REPRODUCIBLE_TEST_INSTRUCTIONS_PRESENT = true
DETERMINISTIC_TESTS_EXECUTED = true
DETERMINISTIC_TESTS_PASS = true
ADK_IMPORT_AND_CONSTRUCTION_PROVEN = true
ADK_LIVE_AGENT_PATH_PROVEN = true
ADK_TOOL_CALL_PROVEN = true
GEMINI_MODEL_ID_CONFIGURED = gemini-3.7-flash
GEMINI_LIVE_CALL_PROVEN = true
CORE_CLARIFICATION_BEHAVIOR_LIVE_GATE_33045663405 = false
CLARIFICATION_REPAIR_IMPLEMENTED = true
CLARIFICATION_REPAIR_LIVE_RETESTED = false
FIRESTORE_ADAPTER_PRESENT = true
FIRESTORE_LIVE_USE_PROVEN = false
CLOUD_RUN_TARGET_CONFIGURED = true
CLOUD_RUN_DEPLOYMENT_PROVEN = false
HOSTED_URL_AVAILABLE = false
VERIFIED = false
```

Evidence:

- deterministic baseline: [`evidence/CI_RUN_33043470358.md`](evidence/CI_RUN_33043470358.md)
- first live infrastructure failure: [`evidence/LIVE_GEMINI_GATE_RUN_33045200154_FAILURE.md`](evidence/LIVE_GEMINI_GATE_RUN_33045200154_FAILURE.md)
- first successful live Gemini/ADK path with behavioral finding: [`evidence/LIVE_GEMINI_GATE_RUN_33045663405.md`](evidence/LIVE_GEMINI_GATE_RUN_33045663405.md)
- live validation procedure: [`docs/LIVE_VALIDATION.md`](docs/LIVE_VALIDATION.md)

The live model path is proven. The core clarification behavior must still pass the repaired live gate before it can be claimed as behaviorally demonstrated.
