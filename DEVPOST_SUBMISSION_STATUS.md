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
| Judge-facing web demo | Live at `https://gen-lang-client-0554159756.web.app`; boundary self-test reports 14/14 in the visitor's own browser | YES, publicly hosted |
| Firebase Hosting used | Deployed 2026-08-28 via the Hosting REST API; release `1787960633912000` serves HTTP 200 | YES, deploy proven |
| Firebase AI Logic used | Human-observed on 2026-08-28: an ordinary browser ran a clear request end to end and Gemini 3.7 Flash returned a drafted executive summary | YES, live browser path proven |
| Cloud Run used | Container and target are ready, but project billing is disabled | NO; live deployment blocked by billing |
| Hosted project URL | `https://gen-lang-client-0554159756.web.app` | YES |
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
FIREBASE_PROJECT_ENABLED = true
FIREBASE_WEB_APP_REGISTERED = true          # 1:503028669213:web:57b1eb16a702d69fd0dff4
FIREBASE_HOSTING_DEPLOYMENT_PROVEN = true   # release 1787960633912000, HTTP 200
HOSTED_URL_AVAILABLE = true                 # gen-lang-client-0554159756.web.app
APP_CHECK_ENFORCED = true                   # firebaseml.googleapis.com
APP_CHECK_SITE_KEY_WIRED = true             # reCAPTCHA Enterprise, domain-bound
BROWSER_BOUNDARY_SELFTEST_LIVE = 14/14      # observed on the deployed page
FIREBASE_AI_LOGIC_LIVE_DEMO_PROVEN = true   # human-observed 2026-08-28
VERIFIED = false
PROMOTED = false
```

## How the live browser path was confirmed

App Check is enforced on `firebaseml.googleapis.com` using reCAPTCHA Enterprise
in SCORE mode. That provider exists to score out automated browsers, so a
scripted browser cannot obtain a token by design and every Gemini call from one
returns 401. This row could never be closed by automation, and automating it
would have meant defeating the control it depends on.

It was closed by observation instead. On 2026-08-28 the deployed URL was opened
in an ordinary browser and the "Clear bounded task" example produced a real
Gemini 3.7 Flash response — a drafted executive summary, ending with the model's
own note that nothing had been sent or published.

One earlier attempt in the same session returned `500 ... stopped before the
operation could complete`. That is a transient provider error, not the App Check
401 that automation hits, and the page reported it as a failure rather than
presenting an answer it had not received.

```text
AUTOMATION_BLOCKED != MISCONFIGURED
NO_TOKEN_FROM_A_BOT = APP_CHECK_WORKING_AS_DESIGNED
HUMAN_OBSERVATION != INDEPENDENT_VERIFICATION
```

The last line matters. One person watching a screen is how this row was closed,
and that is weaker than a second party reproducing it. The claim is "a live call
was observed", not "the behaviour is verified".

Evidence:

- deterministic baseline: [`evidence/CI_RUN_33043470358.md`](evidence/CI_RUN_33043470358.md)
- live Gemini/ADK path: [`evidence/LIVE_GEMINI_GATE_RUN_33045663405.md`](evidence/LIVE_GEMINI_GATE_RUN_33045663405.md)
- successful deterministic pre-model live boundary: [`evidence/LIVE_INTENT_BOUNDARY_RUN_33076307241.md`](evidence/LIVE_INTENT_BOUNDARY_RUN_33076307241.md)
- live Firestore write/read/delete gate: [`evidence/FIRESTORE_LIVE_GATE_2026-08-27.md`](evidence/FIRESTORE_LIVE_GATE_2026-08-27.md)
- judge demo/container CI: [`evidence/CI_RUN_33083223395_JUDGE_DEMO_CONTAINER.md`](evidence/CI_RUN_33083223395_JUDGE_DEMO_CONTAINER.md)
- zero-billing Firebase Hosting surface: `public/`, `firebase.json`, `firestore.rules`
- zero-billing judge-demo CI: GitHub Actions run `33087777218`, commit `3b0c7f9ba30e85288b5ce63dc7cc2be3e1cad451`, conclusion `success`

The live Gemini model path, deterministic pre-model intent boundary and live Firestore persistence path are proven. The judge demo now has both a Cloud Run-capable FastAPI path and a no-billing Firebase Hosting browser path. Billing-disabled Cloud Run is not claimed. Firebase Hosting / Firebase AI Logic remain unproven until the existing Google Cloud project is Firebase-enabled, the Web App/App Check configuration is completed, and a live URL passes smoke tests.
