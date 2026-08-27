# Live IntentGuard Gate — Run 33046624824

Date: 2026-08-27
Subject commit: `53da5812829c9f36d7243052ab290eec680eb6ca`
Workflow: `live-gemini-gate`
Conclusion: `FAILURE`

## What passed

- `GEMINI_API_KEY` secret was present and not printed.
- Dependency installation passed.
- Deterministic suite passed: `13 passed`.
- The live ADK/Agents CLI execution step completed successfully against `gemini-3.7-flash`.

## What failed

The hardened behavioral step required a `compile_human_intent` tool call and the expected clarification evidence. In this run the model produced no tool call, so the behavioral evidence check failed.

This is not evidence that the deterministic clarification repair regressed. The same subject passed its 13 deterministic tests. It is evidence that an instruction telling an LLM to always call a safety/intention tool is not itself a reliable enforcement mechanism.

## Architectural consequence

The intent boundary is being moved from optional model tool-selection into an ADK `before_model_callback` so that material ambiguity is compiled and stopped before model reasoning.

```text
PROMPT_INSTRUCTION != ENFORCEMENT_BOUNDARY
MODEL_TOOL_SELECTION != DETERMINISTIC_GUARD
MATERIAL_AMBIGUITY => PRE_MODEL_INTENT_COMPILATION
```

## Truth boundary

```text
GEMINI_LIVE_CALL_PREVIOUSLY_PROVEN = true
ADK_LIVE_PATH_PROVEN = true
DETERMINISTIC_CLARIFICATION_REPAIR_CI_PROVEN = true
LIVE_TOOL_SELECTION_RELIABLE = false
PRE_MODEL_BOUNDARY_LIVE_PROVEN = false
VERIFIED = false
```
