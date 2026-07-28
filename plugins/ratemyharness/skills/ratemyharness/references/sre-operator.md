# SRE and runtime-operator review

Use this route to decide whether operators can detect, control, recover, and safely change the harness under real load and dependency failure.

## Operational contract

Record service-level objectives for successful task completion, latency, cancellation, recovery, and cost. Define ownership for the harness, model provider, tools, queues, state stores, and incidents.

## Review matrix

| Area | Evidence to seek | Failure pattern |
|---|---|---|
| Time budgets | model, tool, queue, wall-clock, token, and cost deadlines | one timeout exists only at the HTTP edge |
| Retry | typed policy, attempt IDs, backoff, jitter, caps, retry budget | retries multiply across layers |
| Cancellation | durable request and propagation to every active component | cancelled runs keep spending or writing |
| Queueing | leases, visibility timeout, deduplication, backpressure, dead letter | two workers own one run or poison work loops forever |
| Checkpoints | atomic versioned state and replay-safe resume | crash replays committed effects |
| Observability | run/session/attempt/tool-call IDs, structured events, terminal reason | uncorrelated `starting`, `retrying`, `done` logs |
| Metrics | task success, unsafe effects, latency percentiles, cost, retries, saturation | provider uptime is used as product reliability |
| Alerts | symptom and invariant alerts with runbooks | alert on log volume without user impact |
| Rollout | versioned prompts/config, canary, compatibility, rollback | in-flight runs change semantics mid-run |
| Recovery | replay, reconciliation, dead-letter handling, incident exercise | backup exists but restore is untested |

For `public-release`, `privileged-production`, and `high-stakes`, bind drift metrics, canary comparisons, and rollback signals to the exact harness/build, model, prompt, tool-schema, retrieval/data, dataset, rubric, and judge identity. Do not impose online monitoring or canary requirements on local prototypes or team-only reviews.

## Failure injection

Exercise provider rate limits, slow or malformed tools, ambiguous timeouts, queue redelivery, worker death, state-store outage, context overflow, expired approval, cancellation during a tool, and process restart after a side effect. Use bounded synthetic fixtures.

Verify the trace can answer: who initiated the action, what authority was evaluated, which attempt ran, what external effect committed, why the run terminated, and how it can be safely resumed or reconciled.

## Verdict discipline

Do not call a harness production-ready because a happy-path smoke test passes. Missing structured telemetry or recovery evidence is normally `INSUFFICIENT EVIDENCE`; a verified unsafe retry, runaway loop, or fabricated terminal state activates the corresponding veto.
