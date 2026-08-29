# Video script — YAXCHÉ IntentGuard (English, max 4 minutes)

Status: `PREPARED_NOT_RECORDED`. Show only what is visible on screen; use the reported human Gemini observation only if the response is visible during recording.

## 0:00–0:25 — Problem

“Many agents make a plausible guess and then act as if the guess were authorization. YAXCHÉ IntentGuard prevents that mistake before model reasoning.”

Show the public URL and **Ambiguous send**.

## 0:25–1:15 — Safe brake and visible evidence

Click Analyze intent.

“The request becomes IntentIR. Recipient and execution authorization are materially ambiguous, so IntentGuard stops before Gemini and asks one precise question. The evidence surface labels what happened in this browser and what is only supported elsewhere.”

Show IntentIR, the stop, contrast panel, and evidence badges.

## 1:15–2:00 — Bounded collaboration

Choose **Clear bounded task** and Analyze.

“When every reading leads to the same safe assistance, the boundary gets out of the way. Firebase AI Logic prepares Gemini 3.7 Flash. I only claim a live answer when it is visible in this browser.”

Show the runtime badge and response panel; show a safe error as an error, not a success.

## 2:00–3:00 — Feedback changes a plan, not the world

Enter: “Ask one precise question at a time.” Click **Apply feedback to plan (local only)**.

“Feedback changes IntentPlan from version one to version two. The plan declares external actions NONE and session-local persistence. It adapts collaboration without sending, deleting, publishing, or saving automatically.”

Show Plan v2 and the separate Firestore save button.

## 3:00–3:40 — Google stack and reproducibility

“Google ADK supplies the Python agent and reusable pre-model guardrail. Firebase Hosting serves this demo. Firebase AI Logic exposes Gemini, and protected Firestore is reserved for an explicit second click. The repository includes deterministic tests, browser-to-Python parity, and a boundary benchmark measuring both catches and false stops.”

Show the README commands, benchmark artifact, and status file.

## 3:40–4:00 — Close

“YAXCHÉ IntentGuard turns ambiguity into a reviewable question and turns feedback into a safe next plan. It never confuses feedback with permission. Thank you.”