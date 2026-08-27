# ESPEJO / Concilio Red-Team Pass 001 — Repair retest PASS

- Original frozen subject: `main@67d381ec8829066211b1430656b29142b55a5d62`
- Repair candidate SHA: `6362f4e8f2199b62d07bf234883c1475dbafb52b`
- Draft PR: `#1`
- GitHub Actions run: `33105818120`
- Job: `unit-tests` / `98635242365`
- Deterministic unit tests: `28 passed / 0 failed`
- Static judge JavaScript syntax: `PASS`
- ADK app import: `PASS`
- Judge web surface import: `PASS`
- Cloud Run container build: `PASS`
- External destructive side effects: `0`
- VERIFIED: `false`
- PROMOTED: `false`

## Failure -> repair -> regression chain

The first clean adversarial attack run (`33105386707`) reproduced five authorization-boundary failures. The repair broadened deterministic recognition for:

- explicit negative/withheld authorization;
- future/conditional approval;
- tentative delegated authority;
- permission euphemisms (`allowed`, `permitted`, `approved`);
- action inflections (`sending`, `emailing`, etc.);
- authorization inflections (`authorized`, `authorizing`, `authorization`);
- dotted recipients such as email addresses inside bounded uncertainty spans.

The exact adversarial cases remain permanent unit tests. After two intermediate repair attempts exposed additional regression/boundary defects, repair SHA `6362f4e8...` passed all 28 unit tests and the full existing CI steps in job `98635242365`.

## Epistemic boundary

This is evidence that the tested repair candidate defeated ESPEJO pass 001 under the deterministic CI suite. It is not proof of general robustness, independent verification, live Firebase behavior, or promotion readiness.

```text
FIRST_ATTACK_RUN_FAIL = true
REPAIR_RETEST_PASS = true
REPAIR_SHA != ORIGINAL_SUBJECT_SHA
CI_PASS != VERIFIED
CI_PASS != PROMOTED
NEXT_REDTEAM_ROUND_REQUIRED = true
```
