# Devpost Submission Status

This file prevents draft-form fields from being confused with evidence-backed implementation claims.

| Devpost field | Current repository evidence | May claim now? |
|---|---|---|
| Code repo URL | Public repository exists | YES |
| Reproducible testing instructions in README | Present in `README.md` | YES |
| Google ADK used | `app/agent.py` uses ADK; CI imported and constructed the agent successfully | YES, implementation-level use proven |
| Gemini 3.5+ used | `gemini-3.5-flash` is configured and accepted at ADK construction | NOT YET as live model use; live inference evidence still required |
| Cloud Run used | `agents-cli-manifest.yaml` targets Cloud Run | NOT YET; deployment evidence required |
| Firestore used | Firestore adapter and dependency are present | NOT YET; live Firestore evidence required |
| Hosted project URL | None yet | NO |
| Architecture diagram | Design artifact exists | YES as architecture design, not deployment proof |
| Reproducible tests passed | CI run `33043470358` | YES: 10 passed |

## Current truth

```text
REPOSITORY_CREATED = true
REPRODUCIBLE_TEST_INSTRUCTIONS_PRESENT = true
DETERMINISTIC_TESTS_EXECUTED = true
DETERMINISTIC_TESTS_PASS = true
DETERMINISTIC_TEST_COUNT = 10
ADK_IMPORT_AND_CONSTRUCTION_PROVEN = true
GEMINI_MODEL_ID_CONFIGURED = gemini-3.5-flash
GEMINI_LIVE_CALL_PROVEN = false
FIRESTORE_ADAPTER_PRESENT = true
FIRESTORE_LIVE_USE_PROVEN = false
CLOUD_RUN_TARGET_CONFIGURED = true
CLOUD_RUN_DEPLOYMENT_PROVEN = false
HOSTED_URL_AVAILABLE = false
VERIFIED = false
```

Evidence: [`evidence/CI_RUN_33043470358.md`](evidence/CI_RUN_33043470358.md).

Update this file whenever evidence changes. Do not infer one field from another.
