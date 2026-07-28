# Optional numeric scoring

Read this reference only when the user requests a numeric grade, comparison, or release score. The qualitative decision still follows `references/review-contract.md`.

## Contents

- [Run the scorer](#run-the-scorer)
- [Root scorecard fields](#root-scorecard-fields)
- [Nested scorecard interfaces](#nested-scorecard-interfaces)
- [Default rubric](#default-rubric)
- [Score anchors](#score-anchors)
- [Target-required publish checks](#target-required-publish-checks)
- [Gate target scope](#gate-target-scope)
- [Caps and output](#caps-and-output)
- [Rubric fingerprint](#rubric-fingerprint)

## Run the scorer

Create a UTF-8 JSON scorecard and run:

```bash
python3 <skill-directory>/scripts/score_review.py path/to/scorecard.json
```

Use `--pretty` only for indented deterministic JSON. The script uses the Python standard library, writes results to stdout, writes errors to stderr, and returns a non-zero exit code for invalid input.

## Root scorecard fields

| Field | Contract |
|---|---|
| `schema_version` | String `"2"` |
| `mode` | `harness-owner`, `staff-runtime-engineer`, `runtime-engineer`, `red-team`, `adversarial`, `sre-operator`, or `oral-defense` |
| `rubric_id` | Stable non-empty identifier retained for re-review |
| `publish_target` | One target ID from the review contract |
| `dimensions` | One to 32 weighted dimension objects; integer weights total 100 |
| `evidence` | Evidence objects referenced by ID from every verified claim |
| `evidence_lanes` | Exact non-substitutable lanes `deterministic-checks`, `critical-journey-e2e`, `probabilistic-eval`, and `continuous-evidence` |
| `quality_evaluation` | Repeated task-quality summary or an explicit component-limited not-applicable reason |
| `coverage` | Exact objects `runtime`, `failure_recovery`, `clean_deploy`, and `required_artifacts` |
| `gates` | Canonical veto objects from the review contract; may be empty |
| `publish_checks` | At least one explicit required or optional target check |

The scorer rejects unknown fields and evidence IDs. Its validation errors name the failing JSON path and legal values.

## Nested scorecard interfaces

```text
Scorecard = {
  schema_version: "2",
  mode: harness-owner | staff-runtime-engineer | runtime-engineer |
        red-team | adversarial | sre-operator | oral-defense,
  rubric_id: nonempty_string,
  publish_target: local-prototype | team-shared | public-release |
                  privileged-production | high-stakes,
  dimensions: Dimension[1..32],
  evidence: Evidence[0..512],
  evidence_lanes: EvidenceLanes,
  quality_evaluation: QualityEvaluation,
  coverage: Coverage,
  gates: Gate[] from references/review-contract.md,
  publish_checks: PublishCheck[1..]
}

Dimension = {
  id: unique_nonempty_string,
  weight: integer_1_to_100,
  score: integer_0_to_100,
  verification: verified | partial | unverified,
  evidence_ids: unique_existing_evidence_ids
}

Evidence = {
  id: unique_nonempty_string,
  kind: runtime | test | install | deploy | static-analysis | manifest |
        reference | dependency | log | trace | document | eval | metric | claim,
  result: pass | fail | mixed | inconclusive,
  reproducible: boolean,
  fresh: boolean,
  lane: structural | deterministic-checks | critical-journey-e2e |
        probabilistic-eval | continuous-evidence,
  assertion_type: deterministic | probabilistic | mixed | not-applicable,
  identity_sha256?: required_for_probabilistic_and_continuous_evidence
}

EvidenceLane = {
  status: PASS | FAIL | UNVERIFIED | N/A,
  evidence_ids: unique_existing_lane_appropriate_evidence_ids,
  reason?: required_when_N/A
}

EvidenceLanes = {
  deterministic-checks: EvidenceLane,
  critical-journey-e2e: EvidenceLane,
  probabilistic-eval: EvidenceLane,
  continuous-evidence: EvidenceLane
}

QualityEvaluation = {
  applicability: required,
  identity: {
    harness_build, model, prompt, tool_schemas, retrieval_data,
    dataset, rubric
  },
  identity_sha256: sha256_of_identity_and_judge_identity,
  comparison: {
    with_harness: {runs, successes},
    baseline: {runs, successes},
    uplift: {observed, minimum}
  },
  task_success: {observed: 0..1, minimum: 0..1},
  task_success_variance: {
    observed_standard_deviation: 0..1,
    maximum_standard_deviation: 0..1,
    policy: nonempty_string
  },
  unsafe_effect_rate: {observed: 0..1, maximum: 0..1},
  cost_per_success: {observed: nonnegative, maximum: nonnegative, unit},
  latency_ms: {observed_p95: nonnegative, maximum_p95: nonnegative},
  judge: {
    kind: deterministic | llm,
    id, version, digest: sha256,
    calibration_evidence_ids
  },
  evidence_ids: exactly_the_probabilistic_eval_lane_ids
}

QualityEvaluation may instead contain `{applicability: required, reason}` while the probabilistic lane is `UNVERIFIED`, or `{applicability: not-applicable, reason}` while that lane is `N/A`.

Coverage = {
  runtime: {level: full | partial | static | none, evidence_ids},
  failure_recovery: {level: tested | partial | claimed | none, evidence_ids},
  clean_deploy: {level: tested | partial | claimed | none, evidence_ids},
  required_artifacts: {total, resolved, evidence_ids}
}

PublishCheck = {
  id: unique_nonempty_string,
  required: boolean,
  status: pass | fail | unverified,
  evidence_ids: unique_existing_evidence_ids
}
```

Unknown fields, duplicate IDs, non-integer scores, missing evidence links, empty `dimensions` or `publish_checks`, `resolved > total`, or weights not totaling 100 are invalid. `verified` needs reproducible non-claim evidence; `partial` needs at least one evidence ID.

Fresh reproducible evidence of the kinds enforced by the scorer is required for full/partial runtime coverage, tested/partial failure recovery, tested/partial clean deploy, resolved artifacts, passing checks, and fixed-gate retests. Active gates require reproducible non-claim fail/mixed evidence; a claim never becomes machine or runtime evidence merely because it is marked reproducible.

Lane evidence is exclusive: one evidence ID cannot appear in two lanes, and its own `lane` and `assertion_type` must match the panel lane. `structural` evidence can never satisfy a panel lane. `deterministic-checks` accepts deterministic runtime/test/static-analysis/trace evidence; `critical-journey-e2e` accepts deterministic or mixed runtime/test/deploy/trace evidence; `probabilistic-eval` accepts probabilistic or mixed `eval`; and `continuous-evidence` accepts metric/log/trace. This prevents green repository CI from masquerading as behavior, quality, or online proof.

`deterministic-checks` and `critical-journey-e2e` are required at every target. `probabilistic-eval` becomes required at `team-shared`; `continuous-evidence` becomes required at `public-release`. Any lane `FAIL` yields `NOT_READY` unless an active veto yields `BLOCKED`; a required `UNVERIFIED` or `N/A` lane yields `INSUFFICIENT_EVIDENCE`.

A passing probabilistic lane requires equal repeated arms, count-derived task success and uplift, positive minimum uplift, bounded observed standard deviation, and passing unsafe-effect, cost-per-success, and p95-latency thresholds. The scorer recomputes success and uplift from arm counts. A deterministic judge requires a stable ID, version, and SHA-256 digest but no LLM calibration. An LLM judge additionally requires fresh passing calibration eval evidence in the probabilistic lane. Probabilistic and continuous evidence must carry the SHA-256 of the exact evaluation/deployment identity tuple; a model, prompt, tool, retrieval, dataset, rubric, or judge change invalidates that evidence.

Schema v2 is fail-closed and does not infer these fields from a v1 scorecard. To migrate, set `schema_version` to `"2"`; add `lane` and `assertion_type` to every evidence item; add all four `evidence_lanes`; and add `quality_evaluation`, using `not-applicable` only for a genuinely component-limited review. Re-run evidence rather than marking old observations fresh by default.

## Default rubric

Use these weights unless the selected role justifies a declared redistribution:

| Dimension ID | Weight | What earns credit |
|---|---:|---|
| `task-loop-correctness` | 20 | Correct states, call/result correlation, verified completion, deterministic stopping |
| `tool-side-effect-integrity` | 15 | Schema validation, authorization, concurrency control, idempotency, partial-effect handling |
| `context-state-memory` | 10 | Ordering, provenance, truncation, persistence, versioning, session and tenant isolation |
| `failure-recovery-termination` | 15 | Bounded retries, budgets, timeouts, cancellation, checkpoints, safe resume and degraded output |
| `security-authority-isolation` | 15 | Least privilege, sandbox, approvals, trust separation, secrets and data boundaries |
| `reliability-operations` | 10 | Dependency failure, queues, backpressure, rollout, rollback, ownership and recovery |
| `observability-evaluation` | 10 | Correlated redacted traces, cost and latency metrics, reproducible evals and causal value evidence |
| `packaging-maintainability` | 5 | Reproducible install/deploy, configuration, versioning, provenance and accurate docs |

Score each dimension from 0 to 100. Use `verified`, `partial`, or `unverified` for its verification state and supply corresponding evidence IDs. The numeric score describes quality; evidence ceilings, target checks, and in-scope active vetoes decide release readiness.

## Score anchors

- `90–100`: independently verified, resilient, and appropriate for the target
- `75–89`: credible with bounded conditions or minor gaps
- `60–74`: useful only for a narrower target; material risks remain
- `40–59`: fragile, substantially unverified, or missing a critical property
- `0–39`: broken, misleading, unsafe, or unable to enforce its claimed runtime contract

| Target | Readiness threshold |
|---|---:|
| `local-prototype` | 50 |
| `team-shared` | 65 |
| `public-release` | 75 |
| `privileged-production` | 85 |
| `high-stakes` | 90 |

## Target-required publish checks

Every target-required check must set `required: true`. A passing check needs fresh reproducible evidence of an allowed kind.

| Target | Required `publish_checks[].id` | Allowed passing evidence |
|---|---|---|
| `privileged-production` | `sandboxed-authority-and-side-effects` | Runtime, test, or trace |
| `privileged-production` | `retry-idempotency-and-recovery` | Runtime, test, or trace |
| `high-stakes` | Both privileged checks | Same as above |
| `high-stakes` | `independent-domain-review` | Document or test |
| `high-stakes` | `human-control` | Runtime, test, or trace |
| `high-stakes` | `auditability` | Runtime, test, log, or trace |
| `high-stakes` | `incident-response` | Runtime, test, document, or trace |

An unverified required check yields `INSUFFICIENT_EVIDENCE`; a failed required check yields `NOT_READY` unless a blocking veto takes precedence.

## Gate target scope

Each gate requires `id`, `state`, `evidence_ids`, and `retest_evidence_ids`. It may also include `affected_targets`, a non-empty array of unique target IDs.

- Omit `affected_targets` for the backward-compatible behavior: the scorer expands its scope to every target.
- When present, list every target that the proven defect blocks; membership is exact and no hierarchy is inferred.
- The output `active_gates` reports every active gate with its normalized `affected_targets`, while `blocking_gates` reports only those that affect the selected `publish_target`.
- Only `blocking_gates` cap readiness and force `BLOCKED`; `vetoed` is true exactly when that list is non-empty.

A fixed gate still requires fresh reproducible passing retest evidence. Target scope cannot turn weak evidence into a pass or mark an active defect fixed.

## Caps and output

The scorer reports `scores.raw_quality` separately from evidence-limited `scores.publish_readiness`. Readiness is the minimum of raw quality and every applicable cap:

- evidence confidence: `A=100`, `B=89`, `C=69`, `D=49`
- missing team runtime or failure/recovery evidence: `64`
- missing public-or-higher runtime, failure/recovery, clean-deploy, or required-artifact evidence: `69`
- each in-scope active veto: `39`

The output also includes normalized active and blocking gate scopes, the four-lane panel with required and failed lanes, the quality-evaluation identity and summary, applied caps, coverage confidence, distribution evidence gaps, publish checks, target threshold, decision, and `vetoed`. Follow the decision order in `references/review-contract.md`; do not reinterpret the JSON to waive a gate.

## Rubric fingerprint

The scorer hashes `rubric_id`, mode, publish target, and sorted dimension IDs and weights. Preserve those inputs with the scorecard for re-review. A changed fingerprint means a before-and-after numeric delta is not a same-rubric comparison even when both scorecards are valid.
