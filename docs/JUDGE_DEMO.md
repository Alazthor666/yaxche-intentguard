# Judge Demo — YAXCHÉ IntentGuard

## The one-minute story

IntentGuard treats a plausible interpretation as **not** being authorization to act. It first compiles a request into IntentIR. If a material uncertainty could alter the target, recipient, scope, authorization, or reversibility, it stops and asks one precise question.

Public URL: <https://gen-lang-client-0554159756.web.app>

## Demo A — safe brake before the model

Click **Ambiguous send**, then **Analyze intent**.

Expected visible result:

- `status = CLARIFY_BEFORE_EXECUTION`;
- a question about the recipient and/or execution authorization;
- “ambiguous request stopped before Gemini”; and
- the browser self-test shows its own result, rather than a README assertion.

Try **Unsafe delete** as a second contrast. “Please delete it” also stops, including polite wording.

## Demo B — bounded collaboration

Click **Clear bounded task**, then **Analyze intent**.

Expected result:

- IntentIR reports `CLEAR_ENOUGH`;
- the agent only receives a bounded assistance request;
- in an ordinary human browser, Firebase AI Logic may show a Gemini 3.7 Flash response;
- if the live call fails, the UI says so and does not manufacture a model answer.

## Demo C — feedback changes a plan, not the outside world

After analyzing any request, enter:

```text
Ask one precise question at a time.
```

Click **Apply feedback to plan (local only)**.

The visible plan moves from v1 to v2 and shows:

```text
updated_by = EXPLICIT_HUMAN_FEEDBACK
external_actions = NONE
persistence = SESSION_LOCAL_ONLY
```

This is the Collaborative Partner behavior: explicit feedback changes the next collaboration step without remote control, messages, deletions, deployment, or automatic persistence.

**Save feedback separately** is a distinct, explicit Firestore action. It must not be used to claim that the local plan transformation itself wrote data.

## Evidence labels

- `TESTED_REPORTED`: a local test or browser self-test produced a result.
- `HUMAN_PROVEN`: a person observed the protected browser Gemini call and captured evidence.
- `NOT_DEPLOYED`: a configured path such as Cloud Run has not been deployed.
- `VERIFIED`: not claimed unless a separate verifier has reviewed the evidence.