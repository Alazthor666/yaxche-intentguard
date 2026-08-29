# Video script — YAXCHÉ IntentGuard (English, max 4 minutes)

Status: `PREPARED_NOT_RECORDED`. Show only evidence you can see on screen.

## 0:00–0:25 — Problem

“AI assistants often make a plausible guess and then act as if the guess were authorization. YAXCHÉ IntentGuard is a Collaborative Partner designed to stop that mistake before model reasoning.”

Show the public URL and the Ambiguous send example.

## 0:25–1:15 — Safe brake

Click Analyze intent.

“The request is compiled into IntentIR. Recipient and execution authorization are materially ambiguous, so the system pauses and asks one precise question. Gemini is not called for this request.”

Show the IntentIR, clarification card, and browser self-test.

## 1:15–2:05 — Bounded assistance

Choose Clear bounded task and Analyze.

“Here the deterministic boundary finds a bounded request. Firebase AI Logic prepares Gemini 3.7 Flash. If a live response appears, this is the human-observed proof. If it does not, I show the safe failure exactly as it appears.”

Show the runtime badge and response panel. Do not claim a response before it is visible.

## 2:05–3:00 — Feedback changes the plan

Enter: “Ask one precise question at a time.” Click Apply feedback to plan (local only).

“Feedback changes IntentPlan from version one to version two. The plan visibly declares external actions NONE and session-local persistence. This is adaptation without hidden remote execution.”

Show Plan v2 and the separate Save feedback button.

## 3:00–3:40 — Google architecture and evidence

“Google ADK provides the Python agent implementation. Firebase Hosting serves this judge demo. Firebase AI Logic exposes Gemini in the browser, and protected Firestore is reserved for explicitly saved feedback. The repository contains reproducible Python tests and a browser-to-Python parity check.”

Show the repository, README test commands, and evidence/status document.

## 3:40–4:00 — Close

“YAXCHÉ IntentGuard turns ambiguity into a reviewable question, then lets people improve the next plan without confusing feedback with permission. Thank you.”