import { initializeApp } from "https://www.gstatic.com/firebasejs/12.18.0/firebase-app.js";
import { getAuth, signInAnonymously } from "https://www.gstatic.com/firebasejs/12.18.0/firebase-auth.js";
import { getFirestore, addDoc, collection, serverTimestamp } from "https://www.gstatic.com/firebasejs/12.18.0/firebase-firestore.js";
import { getAI, getGenerativeModel, GoogleAIBackend } from "https://www.gstatic.com/firebasejs/12.18.0/firebase-ai.js";
import { initializeAppCheck, ReCaptchaEnterpriseProvider } from "https://www.gstatic.com/firebasejs/12.18.0/firebase-app-check.js";

const config = window.INTENTGUARD_FIREBASE_CONFIG || {};
const sessionId = globalThis.crypto?.randomUUID?.() || `judge-${Date.now()}`;

const $ = (id) => document.getElementById(id);
const requestInput = $("requestInput");
const analyzeBtn = $("analyzeBtn");
const intentOutput = $("intentOutput");
const statusPanel = $("statusPanel");
const agentResponse = $("agentResponse");
const responseTitle = $("responseTitle");
const runtimeBadge = $("runtimeBadge");
const feedbackInput = $("feedbackInput");
const feedbackBtn = $("feedbackBtn");
const feedbackStatus = $("feedbackStatus");
const selfTest = $("selfTest");
const geminiEvidence = $("geminiEvidence");
const boundaryEvidence = $("boundaryEvidence");

let firebaseApp = null;
let auth = null;
let db = null;
let model = null;
let firebaseReady = false;

function concrete(value) {
  return typeof value === "string" && value.length > 0 && !value.startsWith("__");
}

function setBadge(text, kind = "neutral") {
  runtimeBadge.textContent = text;
  runtimeBadge.className = `badge ${kind}`;
}

function normalize(text) {
  return text.trim().replace(/\s+/g, " ");
}

function hasSendAction(lower) {
  return /\b(send|email)\b/.test(lower);
}

function hasExplicitRecipient(lower) {
  return lower.includes("@")
    || /\bsend\b[^.!?]{0,160}\bto\s+\S+/.test(lower)
    || /\brecipient\s+(?:is|=)\s+\S+/.test(lower);
}

function hasAuthorizationUncertainty(lower) {
  return [
    /\b(?:whether|if)\b[^.!?]{0,100}\bauthori[sz]/,
    /\bdo not assume\b[^.!?]{0,120}\bauthori[sz]/,
    /\bdon't assume\b[^.!?]{0,120}\bauthori[sz]/,
    /\bwithout assuming\b[^.!?]{0,120}\bauthori[sz]/,
  ].some((pattern) => pattern.test(lower));
}

function buildIntentIR(text) {
  const request = normalize(text);
  if (!request) {
    return {
      original_request: "(empty request)",
      normalized_goal: "Clarify the user's intended outcome",
      constraints: [],
      unknowns: ["goal"],
      success_criteria: [],
      material_ambiguity: true,
      clarification_question: "What would you like me to accomplish?",
      status: "CLARIFY_BEFORE_EXECUTION",
    };
  }

  const lower = request.toLocaleLowerCase().replace(/[.!?]+$/g, "");
  const generic = new Set([
    "do it", "fix it", "handle it", "handle this", "make it better",
    "take care of it", "take care of this",
  ]);

  if (generic.has(lower) || lower.split(/\s+/).length < 3) {
    return {
      original_request: request,
      normalized_goal: request,
      constraints: [],
      unknowns: ["specific outcome", "target"],
      success_criteria: [],
      material_ambiguity: true,
      clarification_question: "What specific outcome should I produce, and what should I act on?",
      status: "CLARIFY_BEFORE_EXECUTION",
    };
  }

  const constraints = [];
  if (lower.includes(" without ")) constraints.push("contains an explicit 'without' restriction");
  if (lower.includes(" before ")) constraints.push("contains an explicit deadline/order constraint");
  if (lower.includes(" must ")) constraints.push("contains an explicit mandatory condition");
  if (lower.includes("do not assume") || lower.includes("don't assume")) {
    constraints.push("must not infer missing human intent or authorization");
  }

  if (hasSendAction(lower)) {
    const unknowns = [];
    if (!hasExplicitRecipient(lower)) unknowns.push("recipient");
    if (hasAuthorizationUncertainty(lower)) unknowns.push("execution authorization");

    if (unknowns.length) {
      let clarification = "Who should receive it, and are you authorizing me to send it or only to help prepare it?";
      if (unknowns.length === 1 && unknowns[0] === "recipient") clarification = "Who should receive it?";
      if (unknowns.length === 1 && unknowns[0] === "execution authorization") {
        clarification = "Are you authorizing me to send it, or only to help prepare it?";
      }
      return {
        original_request: request,
        normalized_goal: request,
        constraints,
        unknowns,
        success_criteria: [],
        material_ambiguity: true,
        clarification_question: clarification,
        status: "CLARIFY_BEFORE_EXECUTION",
      };
    }
  }

  if (lower.startsWith("delete ") && !/( named | id | path |\/|\\)/.test(lower)) {
    return {
      original_request: request,
      normalized_goal: request,
      constraints,
      unknowns: ["exact deletion target"],
      success_criteria: [],
      material_ambiguity: true,
      clarification_question: "Which exact item should be deleted?",
      status: "CLARIFY_BEFORE_EXECUTION",
    };
  }

  if (lower.startsWith("publish ") && !/( on | to | at )/.test(lower)) {
    return {
      original_request: request,
      normalized_goal: request,
      constraints,
      unknowns: ["publication destination"],
      success_criteria: [],
      material_ambiguity: true,
      clarification_question: "Where should this be published?",
      status: "CLARIFY_BEFORE_EXECUTION",
    };
  }

  return {
    original_request: request,
    normalized_goal: request,
    constraints,
    unknowns: [],
    success_criteria: [],
    material_ambiguity: false,
    clarification_question: null,
    status: "CLEAR_ENOUGH",
  };
}

function renderIntent(intent) {
  intentOutput.textContent = JSON.stringify(intent, null, 2);
  if (intent.material_ambiguity) {
    statusPanel.className = "status-panel block";
    statusPanel.innerHTML = `
      <div class="status-title">Execution paused — material ambiguity</div>
      <div class="status-copy">${escapeHtml(intent.clarification_question)}</div>`;
  } else {
    statusPanel.className = "status-panel clear";
    statusPanel.innerHTML = `
      <div class="status-title">Intent boundary passed</div>
      <div class="status-copy">No material ambiguity detected by the deterministic boundary for this request.</div>`;
  }
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function initializeFirebase() {
  if (!concrete(config.apiKey) || !concrete(config.appId) || !concrete(config.projectId)) {
    setBadge("Boundary demo ready", "warn");
    geminiEvidence.textContent = "Firebase Web App registration still required";
    return;
  }

  try {
    firebaseApp = initializeApp({
      apiKey: config.apiKey,
      authDomain: config.authDomain,
      projectId: config.projectId,
      appId: config.appId,
      messagingSenderId: config.messagingSenderId,
    });

    if (concrete(config.appCheckSiteKey)) {
      initializeAppCheck(firebaseApp, {
        provider: new ReCaptchaEnterpriseProvider(config.appCheckSiteKey),
        isTokenAutoRefreshEnabled: true,
      });
    }

    auth = getAuth(firebaseApp);
    db = getFirestore(firebaseApp);
    const ai = getAI(firebaseApp, { backend: new GoogleAIBackend() });
    model = getGenerativeModel(ai, { model: "gemini-3.7-flash" });
    firebaseReady = true;
    setBadge("Firebase runtime ready", "good");
    geminiEvidence.textContent = "Firebase AI Logic initialized; live call occurs on a clear request";
  } catch (error) {
    console.error(error);
    setBadge("Firebase init failed", "bad");
    geminiEvidence.textContent = "Initialization failed — inspect browser console";
  }
}

async function runAgent(request, intent) {
  if (intent.material_ambiguity) {
    responseTitle.textContent = "Clarification required";
    agentResponse.className = "response blocked";
    agentResponse.textContent = intent.clarification_question;
    boundaryEvidence.textContent = "PASS — ambiguous request stopped before Gemini";
    return;
  }

  responseTitle.textContent = "Collaborative response";
  agentResponse.className = "response ai";

  if (!firebaseReady || !model) {
    agentResponse.textContent = "The deterministic intent boundary passed. Firebase AI Logic is not configured yet, so this build will not claim a Gemini response.";
    return;
  }

  agentResponse.textContent = "Gemini is reasoning over the bounded request…";
  const boundedPrompt = [
    "You are YAXCHÉ IntentGuard, a collaborative AI partner.",
    "The request below has already passed a deterministic intent-boundary check.",
    "Preserve the user's meaning. Distinguish assistance from authorization.",
    "Do not claim that any external action was executed unless explicit runtime evidence exists.",
    "Respond concisely and collaboratively.",
    "",
    `Original request: ${request}`,
    `IntentIR: ${JSON.stringify(intent)}`,
  ].join("\n");

  try {
    const result = await model.generateContent(boundedPrompt);
    const text = result.response.text();
    agentResponse.textContent = text || "Gemini returned no textual response.";
    geminiEvidence.textContent = "PASS — live Gemini 3.7 Flash response returned in judge demo";
  } catch (error) {
    console.error(error);
    agentResponse.textContent = `Gemini call failed safely: ${error?.message || "unknown error"}`;
    geminiEvidence.textContent = "Live call attempted but failed — no success claim made";
  }
}

async function analyze() {
  const request = normalize(requestInput.value);
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing…";
  try {
    const intent = buildIntentIR(request);
    renderIntent(intent);
    await runAgent(request, intent);
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze intent";
  }
}

async function saveFeedback() {
  const feedback = normalize(feedbackInput.value);
  if (!feedback) {
    feedbackStatus.textContent = "Write feedback first.";
    return;
  }
  if (!firebaseReady || !auth || !db) {
    feedbackStatus.textContent = "Firebase feedback runtime is not configured yet.";
    return;
  }

  feedbackBtn.disabled = true;
  feedbackStatus.textContent = "Saving…";
  try {
    if (!auth.currentUser) await signInAnonymously(auth);
    await addDoc(collection(db, "intentguard_public_feedback"), {
      uid: auth.currentUser.uid,
      feedback,
      sessionId,
      pageVersion: "judge-demo-v1",
      createdAt: serverTimestamp(),
    });
    feedbackInput.value = "";
    feedbackStatus.textContent = "Feedback persisted to Firestore. Thank you.";
  } catch (error) {
    console.error(error);
    feedbackStatus.textContent = `Feedback was not persisted: ${error?.message || "unknown error"}`;
  } finally {
    feedbackBtn.disabled = false;
  }
}

function runBoundarySelfTest() {
  const cases = [
    ["Do it", "CLARIFY_BEFORE_EXECUTION"],
    ["I need to send an important report today. Help me do it, but do not assume who should receive it or whether I have authorized sending it.", "CLARIFY_BEFORE_EXECUTION"],
    ["Delete it.", "CLARIFY_BEFORE_EXECUTION"],
    ["Draft a concise executive summary of this project for a hackathon judge. Do not send or publish anything.", "CLEAR_ENOUGH"],
  ];
  const passed = cases.filter(([request, expected]) => buildIntentIR(request).status === expected).length;
  selfTest.textContent = `Boundary self-test ${passed}/${cases.length}`;
  boundaryEvidence.textContent = passed === cases.length
    ? `PASS — ${passed}/${cases.length} browser boundary checks`
    : `FAIL — ${passed}/${cases.length} browser boundary checks`;
}

document.querySelectorAll(".example").forEach((button) => {
  button.addEventListener("click", () => {
    requestInput.value = button.dataset.example;
    requestInput.focus();
  });
});

analyzeBtn.addEventListener("click", analyze);
feedbackBtn.addEventListener("click", saveFeedback);

runBoundarySelfTest();
initializeFirebase();
