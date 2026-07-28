# Runtime and task-quality evidence

Keep two independent judgments. Runtime correctness asks whether the harness enforces its contract; task quality asks how often the model-driven system completes the user's job. Neither result can compensate for the other.

## Four evidence lanes

Report these four lanes in every verdict using exactly `PASS`, `FAIL`, `UNVERIFIED`, or `N/A`:

| Lane ID | What belongs here | Minimum credible evidence |
|---|---|---|
| `deterministic-checks` | Authority, correlation, isolation, idempotency, termination, and truthful-state invariants | deterministic tests, static checks, or exact runtime traces |
| `critical-journey-e2e` | One or two user-critical journeys through the real harness boundary | fresh isolated end-to-end runs with external state asserted |
| `probabilistic-eval` | Repeated task success, unsafe outcomes, cost per success, and latency | version-matched repeated eval summary with declared thresholds and variance |
| `continuous-evidence` | Post-release drift, canary health, rollback signals, and production regressions | fresh metrics, logs, or traces tied to the deployed identity |

Classify every evidence item with its lane and assertion type before assigning it to the panel. Do not reuse one item across lanes or let a green lane substitute for another. Repository unit tests and fixture/schema validation use the `structural` class; even when their kind is `test`, they cannot satisfy deterministic runtime or critical-journey E2E.

Use `N/A` only with a concrete scope reason. Below `public-release`, continuous evidence may be `N/A`. For a component-only loop review, probabilistic evaluation may be `N/A` only when no task-quality or product-value claim is in scope; it cannot support team or public readiness.

## Deterministic runtime plane

Treat authority, correlation, isolation, idempotency, termination, and truthfulness as zero-tolerance invariants. Test them with deterministic assertions before using any model judge. A verified failure marks `deterministic-checks` as `FAIL` and activates the matching veto when reachable for the requested target.

Do not infer deterministic correctness from task success. A harness can complete most tasks while leaking state, duplicating effects, or ignoring cancellation.

## Probabilistic task-quality plane

Run the same representative tasks more than once in isolated contexts. Record:

- the immutable identity tuple: harness/build, model, prompt, tool schemas, retrieval/data, dataset, rubric, and judge, plus its canonical SHA-256;
- equal with-harness and credible-baseline run counts and successes, plus count-derived observed uplift and a positive minimum uplift;
- task-success threshold and count-derived observed rate, plus observed and maximum standard deviation and a variance policy;
- unsafe-effect threshold and observed rate;
- cost per successful task and its threshold;
- end-to-end latency percentile and its threshold.

Prefer a deterministic judge and record its kind, ID, version, and SHA-256 digest. Use an LLM judge only for criteria that cannot be asserted directly; record the same identity fields, calibrate it against a small human-labeled set, and retain that fresh passing eval in the probabilistic lane. An unidentified or uncalibrated LLM judge cannot support `PASS`.

Do not infer task quality from runtime stability. A perfectly bounded and observable harness can still solve only half its tasks; mark `probabilistic-eval` `FAIL` or `UNVERIFIED` without weakening the deterministic result.

## Offline and online scope

Use offline deterministic checks, critical journeys, and repeated evals for local and team targets. Require online drift signals, a bounded canary, and a tested rollback path only for `public-release`, `privileged-production`, and `high-stakes`. Put the same canonical identity SHA-256 on probabilistic and continuous evidence so a harness, model, prompt, tool-schema, retrieval, dataset, rubric, or judge change makes the old evidence fail validation.
