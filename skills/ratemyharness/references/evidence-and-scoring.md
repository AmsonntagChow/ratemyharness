# Evidence, scoring, and release decisions

Use this protocol in every role. The numeric score describes harness quality; the release decision also depends on evidence ceilings, target checks, and fixed vetoes.

## Target ladder

| Target | Minimum evidence expected | Threshold |
|---|---|---:|
| Local prototype | static inspection, one representative bounded run, one failure, and termination evidence | 50 |
| Team shared | fresh isolated end-to-end execution, failure and cancellation tests, and a removal path | 65 |
| Public release | clean install or deploy, representative runtime, failure recovery, operational evidence, docs, and trust materials | 75 |
| Privileged production | sandboxed authority, data-flow, retry/idempotency, isolation, side-effect, recovery, and audit evidence | 85 |
| High stakes | independent domain review, human control, auditability, change approval, and incident exercises | 90 |

Use target IDs `local-prototype`, `team-shared`, `public-release`, `privileged-production`, and `high-stakes`.

Apply these ceilings:

- Static reading alone supports at most `local-prototype`.
- Without a fresh instrumented end-to-end run, do not approve `team-shared` or higher.
- Without fresh failure and cancellation tests, do not approve `team-shared` or higher.
- Without clean install or deploy and complete required operational artifacts, do not approve `public-release` or higher.
- Without exercised authority, side-effect, retry/idempotency, and recovery boundaries, do not approve `privileged-production`.
- Without independent domain review, human control, auditability, and incident exercises, do not approve `high-stakes`.

Missing evidence is not proof of a defect. Preserve raw quality, cap the maximum safe target, and name the cheapest test that can raise the ceiling.

The deterministic scorer enforces these exact target checks:

| Target | Required `publish_checks[].id` | Passing evidence kind |
|---|---|---|
| Privileged production | `sandboxed-authority-and-side-effects` | fresh runtime, test, or trace |
| Privileged production | `retry-idempotency-and-recovery` | fresh runtime, test, or trace |
| High stakes | both privileged checks | same as above |
| High stakes | `independent-domain-review` | fresh document or test |
| High stakes | `human-control` | fresh runtime, test, or trace |
| High stakes | `auditability` | fresh runtime, test, log, or trace |
| High stakes | `incident-response` | fresh runtime, test, document, or trace |

Every target-required check must set `required: true`. `unverified` produces `INSUFFICIENT_EVIDENCE`; `fail` produces `NOT READY` unless a veto also applies.

## Evidence levels

| Level | Meaning | Examples |
|---|---|---|
| E3 — clean-room reproduced | behavior repeats in a fresh isolated environment with the original task and controlled dependencies | end-to-end run, failure injection, cold deploy |
| E2 — machine instrumented | independent machine-produced support | test output, trace, state diff, install log, metric export |
| E1 — static fact | concrete code, config, schema, package, or document fact; runtime consequence may remain inferred | missing max-step check, global shared memory, undeclared egress |
| E0 — claim or guess | author statement, diagram, README number, generic concern, or unavailable evidence | “production ready,” “exactly once,” “40% better” |

Keep severity independent from evidence strength. Complete static proof of an unsafe instruction or reachable path can activate a veto when live execution would itself be harmful, but label broader runtime impact as inference.

## Closed-loop finding

```text
[H-###] [BLOCKER|HIGH|MEDIUM|LOW] Short title
Runtime contract or invariant:
Target:
Preconditions:
Exact reproduction or trace:
Expected:
Actual:
Evidence: E# — exact artifact or observation
Impact:
Suspected cause: explicitly label inference
Minimum fix:
Acceptance test:
Adjacent regression test:
```

“Add observability,” “use idempotency,” or “the loop may hang” is not closed until tied to a specific state transition, effect, reproduction, and acceptance test.

## Default rubric

Use these weights unless the selected role justifies a declared redistribution. Explain inapplicable dimensions and redistribute before scoring.

| Dimension ID | Weight | What earns credit |
|---|---:|---|
| `task-loop-correctness` | 20 | correct states, call/result correlation, verified completion, deterministic stopping |
| `tool-side-effect-integrity` | 15 | schema validation, authorization, concurrency control, idempotency, partial-effect handling |
| `context-state-memory` | 10 | ordering, provenance, truncation, persistence, versioning, session and tenant isolation |
| `failure-recovery-termination` | 15 | bounded retries, budgets, timeouts, cancellation, checkpoints, safe resume and degraded output |
| `security-authority-isolation` | 15 | least privilege, sandbox, approvals, trust separation, secrets and data boundaries |
| `reliability-operations` | 10 | dependency failure, queues, backpressure, rollout, rollback, ownership and recovery |
| `observability-evaluation` | 10 | correlated redacted traces, cost and latency metrics, reproducible evals and causal value evidence |
| `packaging-maintainability` | 5 | reproducible install/deploy, configuration, versioning, provenance and accurate docs |

Score each 0–100:

- 90–100: independently verified, repeatable, and appropriate for the target
- 75–89: credible with bounded conditions or minor gaps
- 60–74: useful for a narrower target; material risk remains
- 40–59: fragile, substantially unverified, or missing a critical property
- 0–39: broken, misleading, unsafe, or behaviorally worthless in this dimension

## Operational value differential

Compare `with_harness` and `baseline` in isolated contexts. Keep request, model, tools, data, permissions, and stopping condition constant. Use hidden task assertions and verify external state.

Report task success, unsafe effects, user interventions, latency, token/tool cost, recovery, and reproducibility. Drop assertions both arms always satisfy. A clean architecture is not proof of uplift.

## Fixed vetoes

These verified conditions block the affected target regardless of score:

- `unauthorized-tool-or-side-effect`
- `secret-or-cross-boundary-data-leak`
- `untrusted-content-controls-runtime`
- `sandbox-or-approval-bypass`
- `unbounded-or-uncancellable-loop`
- `duplicate-non-idempotent-effect`
- `fabricated-tool-or-completion-state`
- `unsafe-code-execution`
- `hidden-network-or-telemetry`
- `broken-core-runtime`
- `license-or-provenance-breach`

No measurable improvement over a plain loop is normally `NOT READY`, not a veto. Risk acceptance does not fix a veto; require a fresh same-path passing retest.

## Scorecard contract

Create JSON and run `scripts/score_review.py`. The scorer validates evidence links, weights, target checks, veto state, and a rubric fingerprint.

```json
{
  "schema_version": "1",
  "mode": "staff-runtime-engineer",
  "rubric_id": "ratemyharness/default-v1",
  "publish_target": "public-release",
  "dimensions": [
    {
      "id": "overall",
      "weight": 100,
      "score": 70,
      "verification": "partial",
      "evidence_ids": ["e-runtime", "e-failure", "e-deploy", "e-artifacts"]
    }
  ],
  "evidence": [
    {"id": "e-runtime", "kind": "runtime", "result": "mixed", "reproducible": true, "fresh": true},
    {"id": "e-failure", "kind": "test", "result": "mixed", "reproducible": true, "fresh": true},
    {"id": "e-deploy", "kind": "install", "result": "pass", "reproducible": true, "fresh": true},
    {"id": "e-artifacts", "kind": "reference", "result": "pass", "reproducible": true, "fresh": true}
  ],
  "coverage": {
    "runtime": {"level": "partial", "evidence_ids": ["e-runtime"]},
    "failure_recovery": {"level": "partial", "evidence_ids": ["e-failure"]},
    "clean_deploy": {"level": "tested", "evidence_ids": ["e-deploy"]},
    "required_artifacts": {"total": 8, "resolved": 8, "evidence_ids": ["e-artifacts"]}
  },
  "gates": [],
  "publish_checks": [
    {"id": "representative-runtime", "required": true, "status": "pass", "evidence_ids": ["e-runtime"]}
  ]
}
```

The compact example is valid. A real review should use the eight dimensions or a declared role-specific redistribution totaling 100. The scorer rejects unknown fields and unknown evidence IDs.

## Decision order

1. Active veto -> `BLOCKED`
2. Required check failure -> `NOT READY`
3. Required evidence missing -> `INSUFFICIENT_EVIDENCE`
4. Evidence-limited score below threshold -> `NOT READY`
5. Optional gaps only -> `READY WITH CONDITIONS`
6. All required checks and evidence pass -> `READY`

## Re-review

Preserve rubric ID, target, harness version, model and tool versions, dimension IDs and weights, fixtures, traces, assertions, and finding IDs. Re-run original failures plus adjacent negatives. Show raw quality, success, safety, cost, and readiness deltas separately.
