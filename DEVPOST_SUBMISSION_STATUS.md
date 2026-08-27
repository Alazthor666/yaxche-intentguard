# Devpost Submission Status

This file prevents draft-form fields from being confused with evidence-backed implementation claims.

| Devpost field | Current repository evidence | May claim now? |
|---|---|---|
| Code repo URL | Public repository exists | YES |
| Reproducible testing instructions in README | Present in `README.md` | YES |
| Google ADK used | ADK implementation/configuration is being added in this repository | ONLY AFTER CI/import or live run evidence |
| Gemini 3.5+ used | Model target is `gemini-3.5-flash` | ONLY AFTER live model-call evidence |
| Cloud Run used | Deployment target/config may be present | ONLY AFTER real deployment evidence |
| Firestore used | Adapter may be present | ONLY AFTER real Firestore integration evidence |
| Hosted project URL | None yet | NO |
| Architecture diagram | Design artifact exists / being versioned | YES as design, not deployment proof |
| Reproducible tests passed | Tests will exist | ONLY AFTER CI/local evidence |

## Current truth

```text
REPOSITORY_CREATED = true
REPRODUCIBLE_TEST_INSTRUCTIONS_PRESENT = true
ADK_RUNTIME_PROVEN = false
GEMINI_LIVE_CALL_PROVEN = false
FIRESTORE_LIVE_USE_PROVEN = false
CLOUD_RUN_DEPLOYMENT_PROVEN = false
HOSTED_URL_AVAILABLE = false
VERIFIED = false
```

Update this file whenever evidence changes. Do not infer one field from another.
