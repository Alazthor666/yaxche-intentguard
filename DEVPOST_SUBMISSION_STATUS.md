# Devpost Submission Status

This file prevents draft-form fields from being confused with evidence-backed implementation claims.

| Devpost field | Current repository evidence | May claim now? |
|---|---|---|
| Code repo URL | Public repository exists | YES |
| Reproducible testing instructions in README | Present in `README.md` | YES |
| Google ADK used | Live runs exercise the ADK/Agents CLI surface; run `33076307241` passed the pre-model boundary gate | YES |
| Gemini 3.5+ used | Live run `33045663405` executed with `gemini-3.7-flash` | YES, live model path proven |
| Collaborative clarification behavior | Live run `33076307241` stopped material ambiguity before model reasoning | YES for the tested case |
| Firestore used | Human-observed Cloud Shell gate on 2026-08-27 exercised the repository adapter with live write/read/delete | YES |
| Judge-facing web demo | FastAPI path plus zero-billing Firebase Hosting browser surface are implemented and CI-tested | YES as implemented/deployable, NOT YET publicly hosted |
| Firebase Hosting used | `firebase.json`, public surface and restrictive Firestore rules are in repo; CI run `33087777218` passed | NOT YET; live hosting deploy required |
| Firebase AI Logic used | Browser path is implemented for `gemini-3.7-flash` but Firebase Web App/App Check setup is still pending | NOT YET as live demo evidence |
| Cloud Run used | Container and target are ready, but project billing is disabled | NO; live deployment blocked by billing |
| Hosted project URL | None yet | NO |
| Architecture diagram | Design artifact exists | YES as architecture design, not deployment proof |
| Reproducible tests passed | Zero-billing judge demo CI run `33087777218` | YES |

## Current truth

```text
REPOSITORY_CREATED = true
REPRODUCIBLE_TEST_INSTRUCTIONS_PRESENT = true
DETERMINISTIC_TESTS_EXECUTED = true
DETERMINISTIC_TESTS_PASS = true
ADK_IMPORT_AND_CONSTRUCTION_PROVEN = true
ADK_LIVE_AGENT_PATH_PROVEN = true
ADK_TOOL_CALL_PROVEN = true                 # separately observed in run 33045663405
GEMINI_MODEL_ID_CONFIGURED = gemini-3.7-flash
GEMINI_LIVE_CALL_PROVEN = true             # ADK live path, run 33045663405
PRE_MODEL_INTENT_BOUNDARY_IMPLEMENTED = true
PRE_MODEL_INTENT_BOUNDARY_LIVE_PROVEN = true # run 33076307241
CORE_CLARIFICATION_TESTED_CASE = PASS
FIRESTORE_ADAPTER_PRESENT = true
FIRESTORE_DATABASE_CREATED = true
FIRESTORE_LIVE_WRITE_PROVEN = true
FIRESTORE_LIVE_READ_PROVEN = true
FIRESTORE_LIVE_DELETE_PROVEN = true
FIRESTORE_LIVE_USE_PROVEN = true
JUDGE_FASTAPI_SURFACE_IMPLEMENTED = true
CLOUD_RUN_CONTAINER_BUILD_PROVEN = true
CLOUD_RUN_BILLING_ENABLED = false
CLOUD_RUN_DEPLOYMENT_PROVEN = false
ZERO_BILLING_FIREBASE_HOSTING_SURFACE_IMPLEMENTED = true
ZERO_BILLING_FIREBASE_HOSTING_SURFACE_CI_PROVEN = true
FIREBASE_PROJECT_ENABLED = false_or_not_yet_proven
FIREBASE_WEB_APP_REGISTERED = false_or_not_yet_proven
FIREBASE_AI_LOGIC_LIVE_DEMO_PROVEN = false
FIREBASE_HOSTING_DEPLOYMENT_PROVEN = false
HOSTED_URL_AVAILABLE = false
VERIFIED = false
PROMOTED = false
```

Evidence:

- deterministic baseline: [`evidence/CI_RUN_33043470358.md`](evidence/CI_RUN_33043470358.md)
- live Gemini/ADK path: [`evidence/LIVE_GEMINI_GATE_RUN_33045663405.md`](evidence/LIVE_GEMINI_GATE_RUN_33045663405.md)
- successful deterministic pre-model live boundary: [`evidence/LIVE_INTENT_BOUNDARY_RUN_33076307241.md`](evidence/LIVE_INTENT_BOUNDARY_RUN_33076307241.md)
- live Firestore write/read/delete gate: [`evidence/FIRESTORE_LIVE_GATE_2026-08-27.md`](evidence/FIRESTORE_LIVE_GATE_2026-08-27.md)
- judge demo/container CI: [`evidence/CI_RUN_33083223395_JUDGE_DEMO_CONTAINER.md`](evidence/CI_RUN_33083223395_JUDGE_DEMO_CONTAINER.md)
- zero-billing Firebase Hosting surface: `public/`, `firebase.json`, `firestore.rules`
- zero-billing judge-demo CI: GitHub Actions run `33087777218`, commit `3b0c7f9ba30e85288b5ce63dc7cc2be3e1cad451`, conclusion `success`

The live Gemini model path, deterministic pre-model intent boundary and live Firestore persistence path are proven. The judge demo now has both a Cloud Run-capable FastAPI path and a no-billing Firebase Hosting browser path. Billing-disabled Cloud Run is not claimed. Firebase Hosting / Firebase AI Logic remain unproven until the existing Google Cloud project is Firebase-enabled, the Web App/App Check configuration is completed, and a live URL passes smoke tests.
