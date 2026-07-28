# Harness review contract

Use this reference in every review after role and degree are confirmed. It governs evidence, release ceilings, findings, vetoes, decisions, and re-reviews without requiring a numeric score.

## Contents

- [Target ladder](#target-ladder)
- [Evidence levels](#evidence-levels)
- [Evidence lanes](#evidence-lanes)
- [Review record and verdict interfaces](#review-record-and-verdict-interfaces)
- [Operational value differential](#operational-value-differential)
- [Veto contract](#veto-contract)
- [Decision order](#decision-order)
- [Re-review](#re-review)

## Target ladder

| Target ID | Minimum evidence expected |
|---|---|
| `local-prototype` | Static inspection, deterministic checks, one representative bounded journey, one failure, and termination evidence |
| `team-shared` | Fresh isolated critical journey, deterministic failure and cancellation tests, repeated task-quality eval, and a removal path |
| `public-release` | Clean install or deploy, critical journey, repeated task-quality eval, continuous evidence, failure recovery, docs, and trust materials |
| `privileged-production` | Exercised authority, data flow, retry and idempotency, isolation, side effects, recovery, and audit evidence |
| `high-stakes` | Independent domain review, human control, auditability, change approval, and incident exercises |

Apply these evidence ceilings:

- Static reading alone supports at most `local-prototype`.
- Without a fresh instrumented end-to-end run plus fresh failure and cancellation tests, do not approve `team-shared` or higher.
- Without a repeated version-matched task-quality evaluation, do not approve `team-shared` or higher.
- Without a clean install or deploy and complete required operational artifacts, do not approve `public-release` or higher.
- Without fresh drift/canary evidence and a rollback signal, do not approve `public-release` or higher.
- Without exercised authority, side-effect, retry/idempotency, isolation, and recovery boundaries, do not approve `privileged-production`.
- Without independent domain review, human control, auditability, and incident exercises, do not approve `high-stakes`.

Missing evidence is not proof of a defect. Preserve observed quality, cap the maximum safe target, and name the cheapest test that can raise the ceiling.

When even `local-prototype` is unsupported, report `no supported target` rather than inventing a lower tier.

## Evidence levels

| Level | Meaning | Typical evidence |
|---|---|---|
| E3 — clean-room reproduced | Behavior repeats in a fresh isolated environment with the original task and controlled dependencies | End-to-end run, failure injection, cold deploy |
| E2 — machine instrumented | Independent machine-produced support | Test output, trace, state diff, install log, metric export |
| E1 — static fact | Concrete code, config, schema, package, or document fact; runtime consequence may remain inferred | Missing max-step check, global shared memory, undeclared egress |
| E0 — claim or hypothesis | Author statement, diagram, README number, generic concern, or unavailable evidence | “Production ready,” “exactly once,” “40% better” |

Keep severity independent from evidence strength. Complete static proof of a reachable unsafe path can activate a veto when live execution would itself be harmful, but label broader runtime impact as inference.

Calibrate severity by consequence: `BLOCKER` means an active veto or the target's core runtime is unsafe or impossible; `HIGH` means material authority, data, money, reliability, or operational harm; `MEDIUM` means a bounded but real runtime failure; `LOW` means limited impact with a concrete user or operator consequence.

## Evidence lanes

Every verdict must show these independent lanes in this order:

```text
Evidence lanes:
- deterministic-checks: PASS | FAIL | UNVERIFIED | N/A
- critical-journey-e2e: PASS | FAIL | UNVERIFIED | N/A
- probabilistic-eval: PASS | FAIL | UNVERIFIED | N/A
- continuous-evidence: PASS | FAIL | UNVERIFIED | N/A
```

Use lane meanings and admissible evidence from `references/evaluation-evidence.md`. Do not reuse one evidence item across lanes. A lane can neither upgrade nor hide another: deterministic runtime safety and probabilistic task quality remain separate decisions.

`N/A` requires a scope reason. It is allowed for `continuous-evidence` below `public-release`. It is allowed for `probabilistic-eval` only in a component-limited review with no task-quality or product-value claim, and cannot support `team-shared` or higher. A repository's green CI or a valid fixture file belongs only to structural deterministic evidence; it cannot satisfy a critical journey, probabilistic eval, or continuous lane.

## Review record and verdict interfaces

```text
Finding = {
  id: stable H-###,
  severity: BLOCKER | HIGH | MEDIUM | LOW,
  title,
  runtime_contract_or_invariant,
  affected_targets,
  preconditions,
  exact_reproduction_or_trace,
  expected,
  actual,
  evidence: {id: E-###, state: E1 | E2 | E3, exact_artifact_or_observation}[1..],
  impact,
  suspected_cause: explicitly_labeled_inference,
  minimum_fix,
  acceptance_test,
  adjacent_regression_test
}

Unknown = {
  id: stable U-###,
  unresolved_condition,
  why_it_matters,
  missing_evidence,
  cheapest_resolving_test
}

Verdict = {
  verified_findings: Finding[],
  unverified_items: Unknown[],
  evidence_lanes: {
    deterministic-checks,
    critical-journey-e2e,
    probabilistic-eval,
    continuous-evidence
  },
  deterministic_runtime_invariants,
  probabilistic_task_quality,
  requested_target,
  maximum_safe_target,
  decision,
  numeric_score?: only_if_requested,
  evidence_coverage,
  confidence,
  active_gates,
  blocking_gates,
  actions: Action[0..3],
  retest_plan
}
```

Open every completed verdict with an uncapped severity-sorted `Issue list` before any score, evidence discussion, or explanation. Use exactly one plain-language line per verified problem in the form `[H-### · SEVERITY] failure — consequence`; then show a separate uncapped `待验证` list with one line per unknown in the form `[U-### · UNVERIFIED] unknown — consequence`. State explicitly when either list is empty.

Keep fixes, evidence, reproduction, causes, and veto terminology out of the opening bullets. “Add observability,” “use idempotency,” or “the loop may hang” is not a closed finding until tied to a specific state transition, effect, reproduction, and acceptance test. Only `actions` is capped at three.

## Operational value differential

When value is in scope, compare `with_harness` and the simplest credible baseline in isolated contexts with equal run counts. Hold the request and complete identity tuple constant: harness/build, model, prompt, tool schemas, retrieval/data, dataset, rubric, and judge. Record both arms' successes, count-derived observed uplift, a positive minimum uplift, task-success threshold, observed and maximum standard deviation, variance policy, unsafe effects, latency, cost per success, recovery, and reproducibility. Bind the run to the tuple's canonical SHA-256 and drop assertions both arms always satisfy.

Prefer deterministic assertions and identify every judge by kind, ID, version, and SHA-256 digest. When an LLM judge is unavoidable, require fresh calibration against a human-labeled sample in the probabilistic lane. An unidentified or uncalibrated LLM judge leaves `probabilistic-eval` `UNVERIFIED`; a stable runtime cannot upgrade it, and strong task results cannot upgrade a failed deterministic invariant.

No measurable improvement over a plain loop is normally `NOT READY`, not a veto. A clean architecture is not proof of uplift.

## Veto contract

These verified conditions block each affected target regardless of an average or score:

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

```text
Gate = {
  id: recognized_veto_id,
  state: active | fixed,
  evidence_ids: unique E-###[],
  retest_evidence_ids: unique E-###[],
  affected_targets?: nonempty_unique_target_id[]
}
```

Name the affected targets from the target ladder. Do not automatically broaden a narrowly proven failure, but do not narrow it merely to avoid a block. When no narrower scope is established, treat the active veto as affecting every target. Risk acceptance does not fix a veto; require a fresh same-path passing retest.

`active_gates` contains every active gate and its normalized scope; `blocking_gates` is the subset affecting the requested target.

## Decision order

Apply these labels mechanically for the requested target:

1. One or more active vetoes affecting the target -> `BLOCKED`
2. A required target check or evidence lane fails -> `NOT READY`
3. A required check or evidence lane is `UNVERIFIED` or inapplicably marked `N/A` -> `INSUFFICIENT EVIDENCE`
4. Required checks and lanes pass but bounded optional conditions remain -> `READY WITH CONDITIONS`
5. All required checks, lanes, and evidence pass -> `READY`

Never call a vetoed target `NOT READY`, and never present `UNVERIFIED` as a failed fact.

## Re-review

Preserve rubric ID, target, the complete harness/build-model-prompt-tool-schema-retrieval/data-dataset-rubric-judge identity tuple, dimension IDs and weights when present, fixtures, traces, assertions, and finding IDs. Reuse each prior ID with exactly `FIXED`, `PARTIALLY FIXED`, `NOT FIXED`, `REGRESSED`, or `UNVERIFIABLE`; place `UNVERIFIABLE` under `待验证` and never renumber it. Re-run original failures plus adjacent negatives, and show deterministic runtime, probabilistic quality, safety, cost, latency, and readiness deltas separately.
