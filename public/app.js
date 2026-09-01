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
const applyFeedbackBtn = $("applyFeedbackBtn");
const feedbackBtn = $("feedbackBtn");
const feedbackStatus = $("feedbackStatus");
const planOutput = $("planOutput");
const planStatus = $("planStatus");
const selfTest = $("selfTest");
const geminiEvidence = $("geminiEvidence");
const boundaryEvidence = $("boundaryEvidence");
const tourBtn = $("tourBtn");
const tourStatus = $("tourStatus");
const naiveLane = $("naiveLane");
const guardedLane = $("guardedLane");
const decisionTrace = $("decisionTrace");
const epiFact = $("epiFact");
const epiAuth = $("epiAuth");
const epiIndep = $("epiIndep");
const stBoundary = $("stBoundary");
const stGemini = $("stGemini");

function setState(el, state, label) {
  if (!el) return;
  el.className = `state ${state.toLowerCase()}`;
  el.textContent = label || state;
}

function setEpistemic({ fact, auth, indep }) {
  const write = (el, prefix, value, good) => {
    if (!el) return;
    el.innerHTML = `${prefix} <b>${escapeHtml(value)}</b>`;
    el.className = `epi ${good ? "epi-ok" : "epi-warn"}`;
  };
  write(epiFact, "Fact", fact, false);
  write(epiAuth, "Authorization", auth, false);
  write(epiIndep, "Independent verification", indep, false);
}

let firebaseApp = null;
let auth = null;
let db = null;
let model = null;
let firebaseReady = false;
let activeIntent = null;
let activeIntentPlan = null;

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

// Mirrors app/clarification.py. The browser demo must never claim a boundary
// the tested Python core does not implement.
//
// V1.1 atomic vaccines:
//   PRESSURE != AUTHORITY
//   HISTORICAL_DEFAULT != CURRENT_AUTHORIZATION
//   ONE_CLEAR_ATOM != WHOLE_REQUEST_CLEAR
//   RISK_SIGNAL != MATERIAL_AMBIGUITY

const OUTWARD_VERBS = "(?:send|email|message|post|publish|share|transfer|pay|refund|charge|deploy|release|envia|envía|enviar|manda|mandar|publica|publicar|comparte|compartir|transfiere|transferir|paga|pagar|reembolsa|reembolsar|cobra|cobrar|despliega|desplegar)";
const IRREVERSIBLE_VERBS = "(?:delete|remove|drop|wipe|erase|purge|reset|revoke|overwrite|truncate|cancel|terminate|borra|borrar|elimina|eliminar|suprime|suprimir|vacía|vacia|vaciar|revoca|revocar|sobrescribe|sobrescribir|trunca|truncar|cancela|cancelar|termina|terminar)";
const MONEY_VERBS = "(?:pay|transfer|refund|charge|invoice|wire|reimburse|paga|pagar|transfiere|transferir|reembolsa|reembolsar|cobra|cobrar|factura|facturar)";
const ACCESS_VERBS = "(?:share|grant|give|comparte|compartir|otorga|otorgar|da|dar)";

const PRESUMPTION_PATTERNS = [
  /\bas usual\b/i,
  /\bthe usual\b/i,
  /\bsame as always\b/i,
  /\byou know(?: the one)?\b/i,
  /\bdefault (?:account|address|recipient|destination|settings?)\b/i,
  /\bcomo siempre\b/i,
  /\blo habitual\b/i,
  /\bya sabes\b/i,
  /\bcomo ya sabes\b/i,
  /\bde costumbre\b/i,
  /\b(?:la |el )?(?:direcci[oó]n|cuenta|destino|configuraci[oó]n) de siempre\b/i,
];

const PRESSURE_PATTERNS = [
  /\burgent(?:ly)?\b/i,
  /\bright now\b/i,
  /\bno time\b/i,
  /\bdo it now\b/i,
  /\bimmediately\b/i,
  /\basap\b/i,
  /\burgente\b/i,
  /\bahora mismo\b/i,
  /\bno hay tiempo\b/i,
  /\bhazlo ya\b/i,
  /\binmediatamente\b/i,
  /\bperderemos? (?:la )?cuenta\b/i,
];

const SENSITIVE_TARGET_PATTERNS = [
  /\blogs?\b/i,
  /\bdatabase\b/i,
  /\bbase de datos\b/i,
  /\bpasswords?\b/i,
  /\bcontrase(?:ñ|n)as?\b/i,
  /\bcredentials?\b/i,
  /\bcredenciales\b/i,
  /\bconfiguration\b/i,
  /\bconfiguraci[oó]n\b/i,
  /\bpermissions?\b/i,
  /\bpermisos?\b/i,
  /\bproduction\b/i,
  /\bproducci[oó]n\b/i,
  /\baccess\b/i,
  /\bacceso\b/i,
];

// A comma commonly introduces subordinate authorization context, so it stays
// inside the same atom. Independent goals require a semicolon or an explicit
// coordination connector.
const ATOM_SPLIT_RE = /\s*(?:;|\b(?:and|then|also|plus|y|adem[aá]s|tambi[eé]n|luego|por cierto)\b)\s*/i;

function decomposeIntent(request) {
  const text = normalize(request);
  if (!text) return [];
  return text.split(ATOM_SPLIT_RE).map(normalize).filter(Boolean);
}

function matchesAny(lower, patterns) {
  return patterns.some((pattern) => pattern.test(lower));
}

function hasPresumption(lower) {
  return matchesAny(lower, PRESUMPTION_PATTERNS);
}

function hasPressure(lower) {
  return matchesAny(lower, PRESSURE_PATTERNS);
}

function hasSensitiveTarget(lower) {
  return matchesAny(lower, SENSITIVE_TARGET_PATTERNS);
}

function hasUnnegated(lower, verbGroup) {
  const re = new RegExp(`\\b${verbGroup}\\b`, "g");
  let match;
  while ((match = re.exec(lower)) !== null) {
    const window = lower.slice(Math.max(0, match.index - 48), match.index);
    if (/\b(?:do not|don't|never|without|avoid|refrain from|no|nunca|sin|evita|evitar)\b[\w\s,áéíóúñü]{0,30}$/.test(window)) continue;
    return true;
  }
  return false;
}

function hasHighImpactAction(lower) {
  return hasUnnegated(lower, OUTWARD_VERBS)
    || hasUnnegated(lower, IRREVERSIBLE_VERBS)
    || hasUnnegated(lower, MONEY_VERBS)
    || hasUnnegated(lower, ACCESS_VERBS);
}

function hasExplicitRecipient(lower) {
  return lower.includes("@")
    || new RegExp(`\\b${OUTWARD_VERBS}\\b[^.!?]{0,160}\\b(?:to|a|para)\\s+\\S+`).test(lower)
    || /\b(?:recipient|destinatario|destinataria)\s+(?:is|es|=)\s+\S+/.test(lower)
    || /\b(?:with|con)\s+(?:the\s+|el\s+|la\s+)?(?:team|client|customer|group|equipo|cliente|grupo)\b/.test(lower);
}

function hasAuthorizationUncertainty(lower) {
  return [
    /\b(?:whether|if)\b[^.!?]{0,100}\bauthori[sz]/,
    /\bdo not assume\b[^.!?]{0,120}\bauthori[sz]/,
    /\bdon't assume\b[^.!?]{0,120}\bauthori[sz]/,
    /\bwithout assuming\b[^.!?]{0,120}\bauthori[sz]/,
    /\bnot sure\b[^.!?]{0,80}\b(?:allowed|permitted|approved)/,
    /\b(?:si|no s[eé] si)\b[^.!?]{0,100}\bautoriza/,
    /\bno (?:asumas?|supongas?)\b[^.!?]{0,120}\bautoriza/,
    /\bsin (?:asumir|suponer)\b[^.!?]{0,120}\bautoriza/,
  ].some((pattern) => pattern.test(lower));
}

function hasConcreteTarget(lower) {
  return /["'`][^"'`]{2,}["'`]/.test(lower)
    || /(?:^|\s)(?:[a-zA-Z]:)?[/\\][\w.\-/\\]+/.test(lower)
    || /\b[\w.-]+(?:[/\\][\w.-]+)+\b/.test(lower)
    || /\b(?:named|called|id|uuid|ticket|issue|pr|llamado|llamada|folio|archivo|file|rama|branch)\s+\S+/.test(lower);
}

function detectPresumptionStop(lower) {
  if (!hasPresumption(lower) || !hasHighImpactAction(lower)) return null;
  return {
    unknowns: ["current explicit target/recipient/parameters"],
    question: "This request relies on a historical/default assumption. What exact current target, recipient, scope, and parameters should I use?",
  };
}

function detectMoneyStop(lower) {
  if (!hasUnnegated(lower, MONEY_VERBS)) return null;
  const hasAmount = /(?:[$€£¥]\s?\d|\b\d+(?:[.,]\d+)?\s*(?:usd|eur|mxn|dollars?|pesos?|d[oó]lares?)\b)/.test(lower);
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
  const dangling = new RegExp(`^${IRREVERSIBLE_VERBS}\\s+(?:it|this|that|them|those|these|everything|all|eso|esto|aquello|ellos|ellas|todo|todos|todas)\\b`);
  if (dangling.test(lower) || !hasConcreteTarget(lower)) {
    return {
      unknowns: ["exact target of an irreversible action"],
      question: "This cannot be undone. Which exact item should I act on?",
    };
  }
  return null;
}

function detectScopeStop(lower) {
  if (!/\b(?:all|every|everything|entire|whole|todos?|todas?|todo|cada|completo|completa)\b/.test(lower)) return null;
  if (!hasUnnegated(lower, IRREVERSIBLE_VERBS) && !hasUnnegated(lower, OUTWARD_VERBS)) return null;
  if (hasConcreteTarget(lower)) return null;
  return {
    unknowns: ["scope of the affected set"],
    question: "This would affect an unbounded set. Which exact items are in scope?",
  };
}

function detectAccessStop(lower) {
  const grantsAccess = new RegExp(`\\b${ACCESS_VERBS}\\b[^.!?]{0,60}\\b(?:access|permission|rights|acceso|permiso|permisos)\\b`).test(lower);
  const sharesWith = /\b(?:share|comparte|compartir)\b[^.!?]{0,80}\b(?:with|con)\s+\S+/.test(lower);
  if (!grantsAccess && !sharesWith) return null;
  if (!hasUnnegated(lower, ACCESS_VERBS)) return null;
  if (/\b(?:read[- ]only|view(?:er)?|edit(?:or)?|write|admin|owner|comment|solo lectura|lectura|ver|comentar|editar|escritura|administrador|administradora|propietario|propietaria)\b/.test(lower)) return null;
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

  const verb = /\b(?:send|email|message|envia|envía|enviar|manda|mandar)\b/.test(lower) ? "send" : "do";
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

const DETECTORS = [
  ["presumption", detectPresumptionStop, "historical/default context is being used as a current high-impact parameter"],
  ["money", detectMoneyStop, "value would move with an unknown amount or payee"],
  ["irreversible", detectIrreversibleStop, "the action cannot be undone and the target is not named"],
  ["scope", detectScopeStop, "an unbounded quantifier changes how much this touches"],
  ["access", detectAccessStop, "the recipient is known but not what they may do"],
  ["outward", detectOutwardStop, "the effect leaves the agent and the recipient is unknown"],
];

function atomicSignalConstraints(atomsLower) {
  const constraints = [];
  if (atomsLower.length > 1) constraints.push(`atomic intent decomposition applied: ${atomsLower.length} clauses`);
  if (atomsLower.some(hasPressure)) constraints.push("urgency/pressure detected; pressure does not expand authority");
  if (atomsLower.some(hasHighImpactAction)) constraints.push("high-impact action detected; downstream explicit authorization remains required");
  if (atomsLower.some((atom) => hasSensitiveTarget(atom) && hasHighImpactAction(atom))) {
    constraints.push("sensitive target detected; downstream policy/authorization must fail closed");
  }
  if (atomsLower.some(hasPresumption)) {
    constraints.push("historical/default-context language detected; current authorization cannot be inferred");
  }
  return constraints;
}

function analyzeIntentAtoms(request) {
  return decomposeIntent(request).map((atom, index) => {
    const lower = atom.toLocaleLowerCase().replace(/[.!?]+$/g, "");
    let stop = null;
    let rule = null;
    for (const [candidateRule, detect] of DETECTORS) {
      stop = detect(lower);
      if (stop) {
        rule = candidateRule;
        break;
      }
    }
    return {
      index,
      atom,
      pressure_detected: hasPressure(lower),
      presumption_detected: hasPresumption(lower),
      high_impact_action_detected: hasHighImpactAction(lower),
      sensitive_action_detected: hasSensitiveTarget(lower) && hasHighImpactAction(lower),
      material_stop: Boolean(stop),
      boundary_rule: rule,
      unknowns: stop?.unknowns || [],
    };
  });
}

function naiveAgentGuess(lower) {
  if (hasUnnegated(lower, MONEY_VERBS)) {
    return "Assumes the last invoice and the default account, then moves the money.";
  }
  if (hasUnnegated(lower, IRREVERSIBLE_VERBS)) {
    return "Assumes the most recently mentioned item and performs the irreversible action.";
  }
  if (hasUnnegated(lower, ACCESS_VERBS)) {
    return "Assumes a common access level instead of asking what was authorized.";
  }
  if (hasUnnegated(lower, OUTWARD_VERBS)) {
    return "Assumes the most plausible destination and proceeds.";
  }
  return "Proceeds directly — and here that is the right call.";
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
    "take care of it", "take care of this", "sort it out", "deal with it",
    "you know what to do", "hazlo", "arreglalo", "arréglalo", "encargate",
    "encárgate", "hazte cargo", "ya sabes", "tu sabes que hacer", "tú sabes qué hacer",
  ]);

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

  const atoms = decomposeIntent(request);
  const atomsLower = atoms.map((atom) => atom.toLocaleLowerCase().replace(/[.!?]+$/g, ""));
  const constraints = [];

  if (lower.includes(" without ") || lower.includes(" sin ")) constraints.push("contains an explicit 'without/sin' restriction");
  if (lower.includes(" before ") || lower.includes(" antes ")) constraints.push("contains an explicit deadline/order constraint");
  if (lower.includes(" must ") || lower.includes(" debe ")) constraints.push("contains an explicit mandatory condition");
  if (lower.includes("do not assume") || lower.includes("don't assume") || lower.includes("no asumas") || lower.includes("no supongas")) {
    constraints.push("must not infer missing human intent or authorization");
  }
  if (new RegExp(`\\b(?:do not|no)\\s+(?:${OUTWARD_VERBS}|${IRREVERSIBLE_VERBS})\\b`).test(lower)) {
    constraints.push("explicitly forbids an outward or irreversible action");
  }
  constraints.push(...atomicSignalConstraints(atomsLower));

  const uniqueConstraints = [...new Set(constraints)];

  for (let index = 0; index < atomsLower.length; index += 1) {
    if (generic.has(atomsLower[index])) {
      return {
        original_request: request,
        normalized_goal: request,
        constraints: [...uniqueConstraints, `blocking atom ${index + 1}/${atomsLower.length}: generic intent`],
        unknowns: ["specific outcome", "target"],
        success_criteria: [],
        material_ambiguity: true,
        clarification_question: "What specific outcome should I produce, and what should I act on?",
        status: "CLARIFY_BEFORE_EXECUTION",
        boundary_rule: "generic",
        boundary_reason: `generic intent in atomic clause ${index + 1}/${atomsLower.length}`,
      };
    }
  }

  for (const [rule, detect, because] of DETECTORS) {
    for (let index = 0; index < atomsLower.length; index += 1) {
      const stop = detect(atomsLower[index]);
      if (!stop) continue;
      return {
        original_request: request,
        normalized_goal: request,
        constraints: [...uniqueConstraints, `blocking atom ${index + 1}/${atomsLower.length}: ${rule}`],
        unknowns: stop.unknowns,
        success_criteria: [],
        material_ambiguity: true,
        clarification_question: stop.question,
        status: "CLARIFY_BEFORE_EXECUTION",
        boundary_rule: rule,
        boundary_reason: `${because}; atomic clause ${index + 1}/${atomsLower.length}`,
      };
    }
  }

  return {
    original_request: request,
    normalized_goal: request,
    constraints: uniqueConstraints,
    unknowns: [],
    success_criteria: [],
    material_ambiguity: false,
    clarification_question: null,
    status: "CLEAR_ENOUGH",
    boundary_rule: null,
    boundary_reason: "every atomic clause is clear enough; authorization remains separate",
  };
}

function buildIntentPlan(intent, feedback = "", version = 1) {
  return {
    schema: "intentguard.intent_plan.v1",
    version,
    source: "BROWSER_SESSION",
    intent_status: intent.status,
    next_step: intent.material_ambiguity
      ? "ASK_ONE_PRECISE_QUESTION"
      : "PREPARE_BOUNDED_ASSISTANCE",
    feedback_preference: feedback || "No feedback applied yet.",
    updated_by: feedback ? "EXPLICIT_HUMAN_FEEDBACK" : "INITIAL_INTENT_COMPILATION",
    external_actions: "NONE",
    persistence: "SESSION_LOCAL_ONLY",
  };
}

function renderIntentPlan(plan) {
  planOutput.textContent = JSON.stringify(plan, null, 2);
  planStatus.className = "status-panel clear";
  planStatus.innerHTML = `
    <div class="status-title">Plan v${plan.version} — ${escapeHtml(plan.updated_by)}</div>
    <div class="status-copy">${escapeHtml(plan.next_step)} · ${escapeHtml(plan.external_actions)} · ${escapeHtml(plan.persistence)}</div>`;
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

function renderContrast(request, intent) {
  const lower = request.toLocaleLowerCase().replace(/[.!?]+$/g, "");
  naiveLane.className = "lane-body naive-body";
  naiveLane.textContent = naiveAgentGuess(lower);

  guardedLane.className = `lane-body ${intent.material_ambiguity ? "stopped" : "proceeded"}`;
  guardedLane.textContent = intent.material_ambiguity
    ? `Stops and asks: “${intent.clarification_question}”`
    : "Proceeds — no reading of this changes the outcome.";

  const rule = intent.boundary_rule ? intent.boundary_rule.toUpperCase() : "NONE FIRED";
  decisionTrace.innerHTML =
    `<span class="trace-rule">${escapeHtml(rule)}</span>` +
    `<span class="trace-why">${escapeHtml(intent.boundary_reason || "")}</span>`;
}

async function runAgent(request, intent) {
  renderContrast(request, intent);

  if (intent.material_ambiguity) {
    responseTitle.textContent = "Stopped before the model ran";
    agentResponse.className = "response blocked";
    agentResponse.textContent = intent.clarification_question;
    setEpistemic({ fact: "not established", auth: "none", indep: "no" });
    setState(stBoundary, "OBSERVED");
    boundaryEvidence.textContent = "Ambiguity stopped this request before Gemini was called";
    setState(stGemini, "PENDING");
    geminiEvidence.textContent = "Not called — the boundary held";
    return;
  }

  responseTitle.textContent = "Model output — unverified";
  agentResponse.className = "response ai";
  setState(stBoundary, "OBSERVED");
  boundaryEvidence.textContent = "Boundary passed this request; every reading leads to the same action";

  if (!firebaseReady || !model) {
    agentResponse.textContent = "The deterministic intent boundary passed. Firebase AI Logic is not configured yet, so this build will not claim a Gemini response.";
    setState(stGemini, "PENDING");
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
    setState(stGemini, "UNVERIFIED");
    geminiEvidence.textContent = "Live Gemini 3.7 Flash response returned just now, in this browser";
    setEpistemic({ fact: "not established", auth: "none", indep: "no" });
  } catch (error) {
    console.error(error);
    agentResponse.textContent = `Gemini call failed safely: ${error?.message || "unknown error"}`;
    setState(stGemini, "PENDING");
    geminiEvidence.textContent = "Live call attempted and failed — no success claim made";
    setEpistemic({ fact: "not established", auth: "none", indep: "no" });
  }
}

async function analyze() {
  const request = normalize(requestInput.value);
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing…";
  try {
    const intent = buildIntentIR(request);
    activeIntent = intent;
    activeIntentPlan = buildIntentPlan(intent);
    renderIntent(intent);
    renderIntentPlan(activeIntentPlan);
    await runAgent(request, intent);
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze intent";
  }
}

function applyFeedbackLocally() {
  const feedback = normalize(feedbackInput.value);
  if (!activeIntent || !activeIntentPlan) {
    feedbackStatus.textContent = "Analyze a request before changing its plan.";
    return;
  }
  if (!feedback) {
    feedbackStatus.textContent = "Write feedback first.";
    return;
  }
  activeIntentPlan = buildIntentPlan(activeIntent, feedback, activeIntentPlan.version + 1);
  renderIntentPlan(activeIntentPlan);
  feedbackStatus.textContent = "Applied to the session-local plan. Nothing was sent, saved, or executed.";
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

const BOUNDARY_CASES = [
  ["Do it", "CLARIFY_BEFORE_EXECUTION"],
  ["Delete it.", "CLARIFY_BEFORE_EXECUTION"],
  ["I need to send an important report today. Help me do it, but do not assume who should receive it or whether I have authorized sending it.", "CLARIFY_BEFORE_EXECUTION"],
  ["Pay the invoice", "CLARIFY_BEFORE_EXECUTION"],
  ["Share the roadmap doc with the team", "CLARIFY_BEFORE_EXECUTION"],
  ["Delete all the old records", "CLARIFY_BEFORE_EXECUTION"],
  ["Wipe them from the system", "CLARIFY_BEFORE_EXECUTION"],
  ["Grant access to the repo", "CLARIFY_BEFORE_EXECUTION"],
  ["Draft a note for ticket 123 and delete it", "CLARIFY_BEFORE_EXECUTION"],
  ["Email a summary to alice@example.com and publish the post", "CLARIFY_BEFORE_EXECUTION"],
  ["Redacta un correo amable para el cliente y borra los logs de la base de datos", "CLARIFY_BEFORE_EXECUTION"],
  ["Transfer 500 USD to the usual account", "CLARIFY_BEFORE_EXECUTION"],
  ["Draft a concise executive summary of this project for a hackathon judge. Do not send or publish anything.", "CLEAR_ENOUGH"],
  ["Transfer 500 USD to alice@example.com", "CLEAR_ENOUGH"],
  ["Share the roadmap doc with the team as read-only", "CLEAR_ENOUGH"],
  ["Delete the file named archive.zip", "CLEAR_ENOUGH"],
  ["Do not delete anything, just list the files", "CLEAR_ENOUGH"],
  ["Write a haiku about the sea", "CLEAR_ENOUGH"],
  ["Urgent: summarize the meeting notes into three bullets", "CLEAR_ENOUGH"],
  ["Delete the file named archive.zip immediately", "CLEAR_ENOUGH"],
  ["Write the summary in the usual tone", "CLEAR_ENOUGH"],
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

const TOUR = [
  {
    label: "1/3 · Ambiguous — it asks instead of guessing",
    request: "I need to send an important report today. Help me do it, but do not assume who should receive it or whether I have authorized sending it.",
  },
  {
    label: "2/3 · Irreversible — a pronoun is not a target",
    request: "Delete all the old records",
  },
  {
    label: "3/3 · Clear — it gets out of the way",
    request: "Draft a concise executive summary of this project for a hackathon judge. Do not send or publish anything.",
  },
];

async function runTour() {
  tourBtn.disabled = true;
  analyzeBtn.disabled = true;
  try {
    for (const step of TOUR) {
      tourStatus.textContent = step.label;
      requestInput.value = step.request;
      const intent = buildIntentIR(normalize(step.request));
      activeIntent = intent;
      activeIntentPlan = buildIntentPlan(intent);
      renderIntent(intent);
      renderIntentPlan(activeIntentPlan);
      await runAgent(normalize(step.request), intent);
      await new Promise((resolve) => setTimeout(resolve, 2600));
    }
    tourStatus.textContent = "Tour complete. Two stops, one clean pass — try your own request above.";
  } finally {
    tourBtn.disabled = false;
    analyzeBtn.disabled = false;
  }
}

analyzeBtn.addEventListener("click", analyze);
tourBtn.addEventListener("click", runTour);
applyFeedbackBtn.addEventListener("click", applyFeedbackLocally);
feedbackBtn.addEventListener("click", saveFeedback);

runBoundarySelfTest();
initializeFirebase();