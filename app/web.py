"""Judge-facing FastAPI surface for YAXCHÉ IntentGuard.

The web surface keeps the deterministic intent boundary explicit. Materially
ambiguous requests are stopped before Google ADK/Gemini. Clear-enough requests
continue through the ADK Runner. Explicit feedback is persisted through the
configured storage adapter (Firestore in Cloud Run).
"""

from __future__ import annotations

import os
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel, Field

from .agent import MODEL, root_agent
from .clarification import compile_intent
from .storage import record_feedback


APP_NAME = "intentguard_demo"
_SESSION_SERVICE = InMemorySessionService()
_RUNNER = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=_SESSION_SERVICE,
    auto_create_session=True,
)

web_app = FastAPI(
    title="YAXCHÉ IntentGuard",
    description="Clarify human intent before consequential agent action.",
    version="0.1.0",
)


class IntentRequest(BaseModel):
    request: str = Field(min_length=1, max_length=6000)
    session_id: str | None = Field(default=None, max_length=128)


class FeedbackRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    feedback: str = Field(min_length=1, max_length=2000)


async def _run_adk(message: str, session_id: str) -> str:
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=message)],
    )
    final_text: str | None = None
    async for event in _RUNNER.run_async(
        user_id="judge",
        session_id=session_id,
        new_message=content,
    ):
        if not event.is_final_response() or not event.content or not event.content.parts:
            continue
        for part in event.content.parts:
            if part.text:
                final_text = part.text
                break
    if final_text is None:
        raise RuntimeError("ADK run completed without a textual final response")
    return final_text


@web_app.get("/healthz")
def healthz() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "yaxche-intentguard",
        "model": MODEL,
        "storage": os.getenv("INTENTGUARD_STORAGE", "memory"),
    }


@web_app.get("/api/evidence")
def evidence() -> dict[str, object]:
    return {
        "deterministic_intent_boundary": True,
        "google_adk": True,
        "gemini_model": MODEL,
        "firestore_adapter": True,
        "claims": {
            "live_gemini_path_proven": True,
            "live_pre_model_boundary_proven": True,
            "live_firestore_write_read_delete_proven": True,
            "cloud_run_deployment_proven": False,
        },
    }


@web_app.post("/api/intent")
async def inspect_intent(payload: IntentRequest) -> dict[str, object]:
    intent_ir = compile_intent(payload.request)
    session_id = payload.session_id or f"judge-{uuid.uuid4().hex[:20]}"

    if intent_ir.material_ambiguity:
        return {
            "session_id": session_id,
            "phase": "clarification",
            "model_called": False,
            "boundary": "deterministic_pre_model",
            "intent_ir": intent_ir.model_dump(),
            "response": intent_ir.clarification_question,
        }

    try:
        response = await _run_adk(payload.request, session_id=session_id)
    except Exception as exc:  # Keep credentials/provider details out of the UI.
        raise HTTPException(
            status_code=502,
            detail=f"Agent inference is temporarily unavailable ({type(exc).__name__}).",
        ) from exc

    return {
        "session_id": session_id,
        "phase": "collaboration",
        "model_called": True,
        "boundary": "passed",
        "model": MODEL,
        "intent_ir": intent_ir.model_dump(),
        "response": response,
    }


@web_app.post("/api/feedback")
def save_feedback(payload: FeedbackRequest) -> dict[str, object]:
    try:
        stored = record_feedback(payload.session_id, payload.feedback)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Feedback persistence is temporarily unavailable ({type(exc).__name__}).",
        ) from exc
    return {"saved": True, "record": stored}


HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>YAXCHÉ IntentGuard — Judge Demo</title>
  <style>
    :root { color-scheme: dark; --bg:#07100f; --panel:#0d1a18; --line:#24423c; --mint:#7fffd4; --cyan:#6ad8ff; --text:#edf8f5; --muted:#9db8b1; --warn:#ffd479; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:radial-gradient(circle at 15% 0%,#15342d 0,#07100f 38%,#050909 100%); color:var(--text); min-height:100vh; }
    main { max-width:1120px; margin:auto; padding:42px 22px 70px; }
    .hero { display:grid; grid-template-columns:1.35fr .65fr; gap:22px; align-items:stretch; }
    .card { background:rgba(13,26,24,.92); border:1px solid var(--line); border-radius:20px; padding:24px; box-shadow:0 18px 50px rgba(0,0,0,.28); }
    .eyebrow { color:var(--mint); text-transform:uppercase; letter-spacing:.14em; font-size:12px; font-weight:800; }
    h1 { font-size:clamp(34px,6vw,68px); line-height:.96; margin:12px 0 16px; letter-spacing:-.045em; }
    h1 span { color:var(--mint); }
    h2 { margin:0 0 13px; font-size:20px; }
    p { color:var(--muted); line-height:1.55; }
    .badges { display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }
    .badge { padding:7px 10px; border:1px solid var(--line); border-radius:999px; color:#c9e8df; font-size:12px; background:#0a1513; }
    .flow { display:grid; gap:10px; font-size:13px; }
    .flow div { border-left:2px solid var(--mint); padding:8px 12px; background:#0a1513; border-radius:0 10px 10px 0; }
    .workspace { margin-top:22px; display:grid; grid-template-columns:1fr 1fr; gap:22px; }
    textarea { width:100%; min-height:150px; resize:vertical; border:1px solid var(--line); background:#06110f; color:var(--text); border-radius:14px; padding:15px; font:inherit; outline:none; }
    textarea:focus { border-color:var(--mint); box-shadow:0 0 0 3px rgba(127,255,212,.08); }
    button { border:0; border-radius:12px; padding:11px 15px; font-weight:800; cursor:pointer; background:var(--mint); color:#042019; }
    button.secondary { background:#15332e; color:#d8fff3; border:1px solid var(--line); }
    button:disabled { opacity:.55; cursor:wait; }
    .actions { display:flex; flex-wrap:wrap; gap:9px; margin-top:12px; }
    .sample { font-size:12px; }
    pre { white-space:pre-wrap; word-break:break-word; background:#06110f; border:1px solid var(--line); border-radius:14px; padding:15px; min-height:150px; color:#d6f6ed; overflow:auto; }
    .status { min-height:25px; color:var(--cyan); font-size:13px; margin-top:10px; }
    .status.warn { color:var(--warn); }
    .result-title { display:flex; justify-content:space-between; gap:10px; align-items:center; }
    .pill { font-size:11px; border-radius:999px; padding:6px 9px; border:1px solid var(--line); color:var(--muted); }
    .feedback { margin-top:22px; }
    input { width:100%; padding:12px 14px; border-radius:12px; border:1px solid var(--line); background:#06110f; color:var(--text); font:inherit; }
    footer { color:#78938c; text-align:center; font-size:12px; margin-top:30px; }
    @media(max-width:820px){ .hero,.workspace{grid-template-columns:1fr;} }
  </style>
</head>
<body>
<main>
  <section class="hero">
    <div class="card">
      <div class="eyebrow">All Things Agentic · Collaborative Partner</div>
      <h1>YAXCHÉ <span>IntentGuard</span></h1>
      <p>An adaptive collaboration layer that protects human intent before an AI agent acts. Material ambiguity is stopped deterministically before model reasoning; clear requests continue through Google ADK and Gemini.</p>
      <div class="badges">
        <span class="badge">Google ADK</span><span class="badge">Gemini 3.7 Flash</span><span class="badge">Firestore</span><span class="badge">IntentIR</span><span class="badge">Evidence-first</span>
      </div>
    </div>
    <div class="card">
      <h2>Execution boundary</h2>
      <div class="flow">
        <div>1 · Human request</div><div>2 · Deterministic IntentIR</div><div>3 · Material ambiguity gate</div><div>4 · ADK + Gemini only if clear enough</div><div>5 · Explicit feedback → Firestore</div>
      </div>
    </div>
  </section>

  <section class="workspace">
    <div class="card">
      <h2>Try the agent</h2>
      <p>Start with ambiguity, then compare it with a bounded request.</p>
      <textarea id="request">I need to send an important report today. Help me do it.</textarea>
      <div class="actions">
        <button id="run">Inspect intent</button>
        <button class="secondary sample" data-sample="I need to send an important report today. Help me do it.">Ambiguous sample</button>
        <button class="secondary sample" data-sample="Summarize this project update into five concise bullets for hackathon judges. Do not publish or send anything.">Clear sample</button>
      </div>
      <div id="status" class="status"></div>
    </div>

    <div class="card">
      <div class="result-title"><h2>IntentGuard result</h2><span id="phase" class="pill">waiting</span></div>
      <pre id="answer">Run a sample to see the intent boundary, IntentIR and agent response.</pre>
      <details><summary>Structured IntentIR</summary><pre id="ir">{}</pre></details>
    </div>
  </section>

  <section class="card feedback">
    <h2>Collaborative feedback loop</h2>
    <p>After a run, leave explicit feedback. In the deployed demo it is persisted through the Firestore adapter under the current session.</p>
    <input id="feedback" value="Prefer one precise clarification question at a time." />
    <div class="actions"><button id="saveFeedback" class="secondary">Save feedback</button></div>
    <div id="feedbackStatus" class="status"></div>
  </section>

  <footer>YAXCHÉ IntentGuard · New standalone hackathon implementation · Repository and reproducibility evidence available publicly.</footer>
</main>
<script>
let sessionId = null;
const req = document.getElementById('request');
const run = document.getElementById('run');
const status = document.getElementById('status');
const answer = document.getElementById('answer');
const ir = document.getElementById('ir');
const phase = document.getElementById('phase');

document.querySelectorAll('[data-sample]').forEach(b => b.addEventListener('click', () => { req.value = b.dataset.sample; }));

run.addEventListener('click', async () => {
  run.disabled = true; status.className='status'; status.textContent='Compiling human intent…';
  try {
    const r = await fetch('/api/intent', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({request:req.value, session_id:sessionId})});
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || 'Request failed');
    sessionId = data.session_id;
    phase.textContent = data.phase;
    answer.textContent = data.response;
    ir.textContent = JSON.stringify(data.intent_ir, null, 2);
    status.textContent = data.model_called ? `Boundary passed · ${data.model} was invoked through ADK.` : 'Material ambiguity stopped before model reasoning.';
    if (!data.model_called) status.className='status warn';
  } catch (e) { status.className='status warn'; status.textContent=e.message; }
  finally { run.disabled=false; }
});

document.getElementById('saveFeedback').addEventListener('click', async () => {
  const out=document.getElementById('feedbackStatus');
  if (!sessionId) { out.className='status warn'; out.textContent='Run the agent first so a session exists.'; return; }
  out.className='status'; out.textContent='Saving feedback…';
  try {
    const r=await fetch('/api/feedback',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sessionId,feedback:document.getElementById('feedback').value})});
    const data=await r.json(); if(!r.ok) throw new Error(data.detail||'Save failed');
    out.textContent=`Saved via ${data.record.store}.`;
  } catch(e){ out.className='status warn'; out.textContent=e.message; }
});
</script>
</body>
</html>"""


@web_app.get("/", response_class=HTMLResponse)
def index() -> str:
    return HTML
