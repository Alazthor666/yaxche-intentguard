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

// This mirrors app/clarification.py. The browser must never claim a boundary
// the tested Python core does not implement.
//
// Design rule for every check: stop only when two readings of the same sentence
// would lead the agent to act on a different target, recipient, scope, or
// reversibility. Vague is not the same as materially ambiguous.

const OUTWARD_VERBS = "(?:send|email|message|post|publish|share|transfer|pay|refund|charge|deploy|release)";
const IRREVERSIBLE_VERBS = "(?:delete|remove|drop|wipe|erase|purge|reset|revoke|overwrite|truncate|cancel|terminate)";

function hasUnnegated(lower, verbGroup) {
  // "Do not send it" contains `send`, but forbids the action rather than
  // requesting it. Treating that as a request produces exactly the pointless
  // question that makes a clarifying agent unusable.
  const re = new RegExp(`\\b${verbGroup}\\b`, "g");
  let match;
  while ((match = re.exec(lower)) !== null) {
    const window = lower.slice(Math.max(0, match.index - 40), match.index);
    if (/\b(?:do not|don't|never|without|avoid|refrain from|no)\b[\w\s,]{0,25}$/.test(window)) continue;
    return true;
  }
  return false;
}

function hasExplicitRecipient(lower) {
  return lower.includes("@")
    || new RegExp(`\\b${OUTWARD_VERBS}\\b[^.!?]{0,160}\\bto\\s+\\S+`).test(lower)
    || /\brecipient\s+(?:is|=)\s+\S+/.test(lower)
    || /\bwith\s+(?:the\s+)?(?:team|client|customer|group)\b/.test(lower);
}

function hasAuthorizationUncertainty(lower) {
  return [
    /\b(?:whether|if)\b[^.!?]{0,100}\bauthori[sz]/,
    /\bdo not assume\b[^.!?]{0,120}\bauthori[sz]/,
    /\bdon't assume\b[^.!?]{0,120}\bauthori[sz]/,
    /\bwithout assuming\b[^.!?]{0,120}\bauthori[sz]/,
    /\bnot sure\b[^.!?]{0,80}\b(?:allowed|permitted|approved)/,
  ].some((pattern) => pattern.test(lower));
}

function hasConcreteTarget(lower) {
  return /["'`][^"'`]{2,}["'`]/.test(lower)
    || /[/\\][\w.-]+/.test(lower)
    || /\b(?:named|called|id|uuid|ticket|issue|pr)\s+\S+/.test(lower);
}

function detectMoneyStop(lower) {
  if (!/\b(?:pay|transfer|refund|charge|invoice|wire|reimburse)\b/.test(lower)) return null;
  const hasAmount = /(?:[$€£¥]\s?\d|\b\d+(?:[.,]\d+)?\s*(?:usd|eur|mxn|dollars|pesos)\b)/.test(lower);
  const unknowns = [];
  if (!hasAmount) unknowns.push("amount");
  if (!hasExplicitRecipient(lower)) unknowns.push("payee");
  if (!unknowns.length) return null;
  return {
    unknowns,
    question: `Money movement needs both an exact amount and an exact payee. Missing: ${unknowns.join(", ")}.`,
  };
}

function detectIrreversibleStop(lower) {
  if (!hasUnnegated(lower, IRREVERSIBLE_VERBS)) return null;
  const dangling = new RegExp(`^${IRREVERSIBLE_VERBS}\\s+(?:it|this|that|them|those|these|everything|all)\\b`);
  if (dangling.test(lower) || !hasConcreteTarget(lower)) {
    return {
      unknowns: ["exact target of an irreversible action"],
      question: "This cannot be undone. Which exact item should I act on?",
    };
  }
  return null;
}

function detectScopeStop(lower) {
  if (!/\b(?:all|every|everything|entire|whole)\b/.test(lower)) return null;
  if (!new RegExp(`\\b${IRREVERSIBLE_VERBS}\\b|\\b${OUTWARD_VERBS}\\b`).test(lower)) return null;
  if (hasConcreteTarget(lower)) return null;
  return {
    unknowns: ["scope of the affected set"],
    question: "This would affect an unbounded set. Which exact items are in scope?",
  };
}

function detectAccessStop(lower) {
  const grantsAccess = /\b(?:share|grant|give)\b[^.!?]{0,60}\b(?:access|permission|rights)\b/.test(lower);
  const sharesWith = /\bshare\b[^.!?]{0,80}\bwith\s+\S+/.test(lower);
  if (!grantsAccess && !sharesWith) return null;
  if (!hasUnnegated(lower, "(?:share|grant|give)")) return null;
  if (/\b(?:read[- ]only|view(?:er)?|edit(?:or)?|write|admin|owner|comment)\b/.test(lower)) return null;
  return {
    unknowns: ["access level"],
    question: "What level of access should they get — view, comment, edit, or admin?",
  };
}

function detectOutwardStop(lower) {
  if (!hasUnnegated(lower, OUTWARD_VERBS)) return null;
  const unknowns = [];
  if (!hasExplicitRecipient(lower)) unknowns.push("recipient");
  if (hasAuthorizationUncertainty(lower)) unknowns.push("execution authorization");
  if (!unknowns.length) return null;

  const verb = /\b(?:send|email|message)\b/.test(lower) ? "send" : "do";
  let question;
  if (unknowns.length === 1 && unknowns[0] === "recipient") {
    question = "Who should receive it?";
  } else if (unknowns.length === 1 && unknowns[0] === "execution authorization") {
    question = `Are you authorizing me to ${verb} it, or only to help prepare it?`;
  } else {
    question = `Who should receive it, and are you authorizing me to ${verb} it or only to help prepare it?`;
  }
  return { unknowns, question };
}

// Order matters: the most consequential class wins, so the question the user
// sees is about the thing that could hurt most.
const DETECTORS = [
  detectMoneyStop,
  detectIrreversibleStop,
  detectScopeStop,
  detectAccessStop,
  detectOutwardStop,
];

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
    "take care of it", "take care of this", "sort it out", "deal with it",
    "you know what to do",
  ]);

  // Brevity is not ambiguity. "Delete /etc/hosts" is two words and perfectly
  // specific; "handle it" is two words and says nothing.
  const tooShort = lower.split(/\s+/).length < 3 && !hasConcreteTarget(lower);
  if (generic.has(lower) || tooShort) {
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
  if (/\bdo not (?:send|publish|share|delete)\b/.test(lower)) {
    constraints.push("explicitly forbids an outward or irreversible action");
  }

  for (const detect of DETECTORS) {
    const stop = detect(lower);
    if (stop) {
      return {
        original_request: request,
        normalized_goal: request,
        constraints,
        unknowns: stop.unknowns,
        success_criteria: [],
        material_ambiguity: true,
        clarification_question: stop.question,
        status: "CLARIFY_BEFORE_EXECUTION",
      };
    }
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

// Mirrors tests/unit/test_clarification.py. Every case runs in the judge's own
// browser on page load, so the claim is verified in front of them rather than
// asserted in a README.
const BOUNDARY_CASES = [
  // stops
  ["Do it", "CLARIFY_BEFORE_EXECUTION"],
  ["Delete it.", "CLARIFY_BEFORE_EXECUTION"],
  ["Please delete it.", "CLARIFY_BEFORE_EXECUTION"],
  ["I need to send an important report today. Help me do it, but do not assume who should receive it or whether I have authorized sending it.", "CLARIFY_BEFORE_EXECUTION"],
  ["Pay the invoice", "CLARIFY_BEFORE_EXECUTION"],
  ["Share the roadmap doc with the team", "CLARIFY_BEFORE_EXECUTION"],
  ["Delete all the old records", "CLARIFY_BEFORE_EXECUTION"],
  ["Wipe them from the system", "CLARIFY_BEFORE_EXECUTION"],
  ["Grant access to the repo", "CLARIFY_BEFORE_EXECUTION"],
  // continues — a clarifying agent that stops on everything is unusable
  ["Draft a concise executive summary of this project for a hackathon judge. Do not send or publish anything.", "CLEAR_ENOUGH"],
  ["Transfer 500 USD to alice@example.com", "CLEAR_ENOUGH"],
  ["Share the roadmap doc with the team as read-only", "CLEAR_ENOUGH"],
  ["Delete the file named archive.zip", "CLEAR_ENOUGH"],
  ["Do not delete anything, just list the files", "CLEAR_ENOUGH"],
  ["Write a haiku about the sea", "CLEAR_ENOUGH"],
];

function runBoundarySelfTest() {
  const failures = BOUNDARY_CASES.filter(
    ([request, expected]) => buildIntentIR(request).status !== expected,
  );
  const total = BOUNDARY_CASES.length;
  const passed = total - failures.length;
  const stops = BOUNDARY_CASES.filter(([, e]) => e === "CLARIFY_BEFORE_EXECUTION").length;

  selfTest.textContent = `Boundary self-test ${passed}/${total}`;
  boundaryEvidence.textContent = failures.length === 0
    ? `PASS — ${passed}/${total} live in this browser (${stops} stop, ${total - stops} proceed)`
    : `FAIL — ${failures.length} of ${total}: ${failures.map(([r]) => r.slice(0, 30)).join(" | ")}`;
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
