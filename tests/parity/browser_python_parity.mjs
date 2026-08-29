// Parity guard: the browser boundary must agree with the tested Python core.
//
// The judge demo runs its own copy of the clarification logic in JavaScript so
// it works with no backend. That copy is a liability: if it drifts from
// app/clarification.py, the demo shows judges a boundary the tested core does
// not implement.
//
// This harness loads the real public/app.js, strips the DOM and Firebase parts,
// and runs the same corpus that tests/unit/test_clarification.py asserts.
//
//   BROWSER_BOUNDARY_MUST_EQUAL_PYTHON_BOUNDARY
//
// Run:  node tests/parity/browser_python_parity.mjs

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
  .replace(/^const \w+ = \$\(".*"\);$/gm, "")
  .replace(/^const \$ = .*$/gm, "")

  .replace(/^function setBadge[\s\S]*?^}$/gm, "")
  .replace(/^function renderIntent[\s\S]*?^}$/gm, "");
source += "\nexport { buildIntentIR };\n";

const shimPath = path.join(here, ".boundary-under-test.mjs");
fs.writeFileSync(shimPath, source);

let buildIntentIR;
try {
  ({ buildIntentIR } = await import(`file://${shimPath.replace(/\\/g, "/")}`));
} finally {
  fs.rmSync(shimPath, { force: true });
}

// true  = must stop and ask
// false = must proceed; an agent that asks about everything is unusable
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
];

const failures = [];
for (const [request, mustStop] of CASES) {
  const actual = buildIntentIR(request).material_ambiguity;
  if (actual !== mustStop) failures.push({ request, expected: mustStop, actual });
}

for (const f of failures) {
  console.error(`FAIL expected_stop=${f.expected} got=${f.actual} :: ${f.request}`);
}
console.log(`BROWSER_BOUNDARY_PARITY=${CASES.length - failures.length}/${CASES.length}`);
process.exit(failures.length === 0 ? 0 : 1);
