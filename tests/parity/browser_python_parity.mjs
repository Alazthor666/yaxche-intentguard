// Parity guard: the browser boundary must agree with the tested Python core.
//
// The judge demo runs its own copy of the clarification logic in JavaScript so
// it works with no backend. That copy is a liability: if it drifts from
// app/clarification.py, the demo shows judges a boundary the tested core does
// not implement.
//
//   BROWSER_BOUNDARY_MUST_EQUAL_PYTHON_BOUNDARY
//
// Run: node tests/parity/browser_python_parity.mjs

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "..", "..");

globalThis.window = {};
globalThis.document = { getElementById: () => ({}), querySelectorAll: () => [] };

let source = fs.readFileSync(path.join(repoRoot, "public", "app.js"), "utf8");
source = source.split("async function initializeFirebase")[0];
source = source
  .replace(/^import .*$/gm, "")
  .replace(/^const config = .*$/gm, "const config = {};")
  .replace(/^const \$ = .*$/gm, "")
  .replace(/^const \w+ = \$\(.*\);$/gm, "")
  .replace(/^function (setBadge|renderIntent|setState|setEpistemic)[\s\S]*?^}$/gm, "");
source += "\nexport { buildIntentIR, buildIntentPlan };\n";

const shimPath = path.join(here, ".boundary-under-test.mjs");
fs.writeFileSync(shimPath, source);

let buildIntentIR;
let buildIntentPlan;
try {
  ({ buildIntentIR, buildIntentPlan } = await import(`file://${shimPath.replace(/\\/g, "/")}`));
} finally {
  fs.rmSync(shimPath, { force: true });
}

// true = must stop and ask; false = must proceed.
const CASES = [
  ["Do it", true],
  ["Delete it.", true],
  ["Please delete it.", true],
  ["I need to send an important report today. Help me do it, but do not assume who should receive it or whether I have authorized sending it.", true],
  ["Pay the invoice", true],
  ["Share the roadmap doc with the team", true],
  ["Delete all the old records", true],
  ["Reset everything", true],
  ["Grant access to the repo", true],
  ["Publish the post", true],
  ["Wipe them from the system", true],
  ["Refund the customer at billing@example.com", true],

  // V1.1 atomic vaccines: context from one clause cannot launder another.
  ["Draft a note for ticket 123 and delete it", true],
  ["Email a summary to alice@example.com and publish the post", true],
  ["Redacta un correo amable para el cliente y borra los logs de la base de datos", true],
  ["Transfer 500 USD to the usual account", true],
  ["Urgent: send the report now", true],

  ["Draft a concise executive summary of this project for a hackathon judge. Do not send or publish anything.", false],
  ["Transfer 500 USD to alice@example.com", false],
  ["Share the roadmap doc with the team as read-only", false],
  ["Delete the file named archive.zip", false],
  ["Remove build/artifacts/stale.log", false],
  ["Do not delete anything, just list the files", false],
  ["Summarize the meeting notes into three bullets", false],
  ["Write a haiku about the sea", false],
  ["Send the deck to maria@datak.mx", false],
  ["Refactor this function without changing its public API", false],

  // Pressure and risk signals are not themselves ambiguity.
  ["Urgent: summarize the meeting notes into three bullets", false],
  ["Delete the file named archive.zip immediately", false],
  ["Write the summary in the usual tone", false],
  ["Summarize the notes and write a haiku", false],
  ["Do not transfer money; just summarize the invoice", false],
];

const failures = [];
for (const [request, mustStop] of CASES) {
  const actual = buildIntentIR(request).material_ambiguity;
  if (actual !== mustStop) failures.push({ request, expected: mustStop, actual });
}

for (const f of failures) {
  console.error(`FAIL expected_stop=${f.expected} got=${f.actual} :: ${f.request}`);
}
const planV1 = buildIntentPlan(buildIntentIR("Write a haiku about the sea"));
const planV2 = buildIntentPlan(buildIntentIR("Write a haiku about the sea"), "Use one concise question.", 2);
const planFailure = planV1.external_actions !== "NONE"
  || planV1.persistence !== "SESSION_LOCAL_ONLY"
  || planV2.version !== 2
  || planV2.updated_by !== "EXPLICIT_HUMAN_FEEDBACK";
if (planFailure) console.error("FAIL session-local feedback plan contract");
console.log(`BROWSER_BOUNDARY_PARITY=${CASES.length - failures.length}/${CASES.length}`);
console.log(`BROWSER_PLAN_CONTRACT=${planFailure ? "FAIL" : "PASS"}`);
process.exit(failures.length === 0 && !planFailure ? 0 : 1);
