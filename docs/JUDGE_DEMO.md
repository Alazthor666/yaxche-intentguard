# Judge Demo — YAXCHÉ IntentGuard

## Goal

A judge should understand the differentiator in under one minute:

> IntentGuard does not treat a plausible model interpretation as permission to act.

The public web surface is designed around one contrast.

## Demo A — material ambiguity

Paste:

```text
I need to send an important report today. Help me do it.
```

Expected result:

- `phase = clarification`
- `model_called = false`
- `material_ambiguity = true`
- unknown includes `recipient`
- status is `CLARIFY_BEFORE_EXECUTION`
- the UI asks the minimum useful clarification question

This demonstrates that the intent boundary executes before Gemini.

## Demo B — clear bounded collaboration

Paste:

```text
Summarize this project update into five concise bullets for hackathon judges. Do not publish or send anything.
```

Expected result after Cloud Run is configured with Gemini credentials:

- the deterministic boundary passes;
- Google ADK runs the agent;
- Gemini 3.7 Flash returns bounded assistance;
- the UI explicitly reports that the model was called.

## Demo C — explicit feedback persistence

After either run, enter:

```text
Prefer one precise clarification question at a time.
```

and click **Save feedback**.

With `INTENTGUARD_STORAGE=firestore`, the server persists feedback through the Firestore adapter. A separate 2026-08-27 live gate already demonstrated real Firestore write, read-back and deletion in the hackathon Google Cloud project.

## Evidence already established

- deterministic test suite: PASS
- Google ADK import/construction: PASS
- live Gemini 3.7 Flash path: PASS
- live ADK tool call: PASS
- deterministic pre-model ambiguity boundary: PASS for the registered gate case
- live Firestore write/read/delete: PASS

Cloud Run deployment and public URL remain separate claims until a service is actually deployed and smoke-tested.

## Public service acceptance gate

A deployed judge URL is accepted only when all of the following pass:

```text
GET /                 => 200 and contains YAXCHÉ IntentGuard
GET /healthz          => 200, status=ok
POST /api/intent      => ambiguous case stops before model
POST /api/intent      => clear case returns an ADK/Gemini response
POST /api/feedback    => returns saved=true with store=firestore
```

Only then may `HOSTED_URL_AVAILABLE=true` and `CLOUD_RUN_DEPLOYMENT_PROVEN=true` be recorded.
