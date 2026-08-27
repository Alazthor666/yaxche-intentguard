# Live Pre-Model Intent Boundary — Run 33076307241

Date: 2026-08-27
Workflow: `live-gemini-gate`
Subject commit: `47c13ff844514cc0c76b6157f25212258669da9f`
Conclusion: `SUCCESS`

## Proven in this run

- GitHub Actions secret `GEMINI_API_KEY` was present and its value was not printed.
- Google ADK / Agents CLI surface started successfully.
- Deterministic unit suite passed: `15 passed`.
- The same ambiguous report request previously used for live testing was intercepted by the ADK pre-model intent boundary.
- IntentGuard emitted `INTENTGUARD_GATE=CLARIFY_BEFORE_EXECUTION`.
- IntentIR contained `material_ambiguity=true`.
- IntentIR status was `CLARIFY_BEFORE_EXECUTION`.
- IntentIR explicitly identified `recipient` and `execution authorization` as unknowns.
- The emitted clarification question was: `Who should receive it, and are you authorizing me to send it or only to help prepare it?`
- The hardened behavioral evidence step passed.

## Architectural meaning

The material-ambiguity boundary no longer depends on Gemini choosing to call a tool. ADK executes deterministic intent compilation in `before_model_callback`; if ambiguity is material, the model path is short-circuited and the user is asked the minimum clarification question first.

```text
PROMPT_INSTRUCTION != ENFORCEMENT_BOUNDARY
MODEL_TOOL_SELECTION != DETERMINISTIC_GUARD
MATERIAL_AMBIGUITY => PRE_MODEL_INTENT_COMPILATION
```

## Evidence separation

This run proves the live ADK pre-model boundary for the tested case. It is not a new proof that Gemini itself detected the ambiguity, because the callback intentionally stops the model before reasoning on materially ambiguous input.

A real Gemini 3.7 live call through the same agent stack was separately proven in run `33045663405`.

## Current truth after this run

```text
GEMINI_LIVE_CALL_PROVEN = true              # run 33045663405
ADK_LIVE_AGENT_PATH_PROVEN = true
PRE_MODEL_INTENT_BOUNDARY_LIVE_PROVEN = true # run 33076307241
CORE_CLARIFICATION_TESTED_CASE = PASS
DETERMINISTIC_TEST_COUNT = 15
FIRESTORE_LIVE_USE_PROVEN = false
CLOUD_RUN_DEPLOYMENT_PROVEN = false
HOSTED_URL_AVAILABLE = false
VERIFIED = false
PROMOTED = false
```
