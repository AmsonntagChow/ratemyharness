# Staff agent-runtime engineer review

Use this route for implementation correctness and maintainability. Reconstruct behavior from code, configuration, schemas, tests, and traces; do not infer a complete runtime from one loop function.

## State machine first

Document the run states and legal transitions. At minimum cover queued, running, waiting for approval, waiting for tool, cancelled, failed, exhausted, and completed. Verify terminal states are mutually exclusive and durable.

Trace identifiers across model response, tool call, tool attempt, tool result, state update, checkpoint, and final response. Late, duplicate, missing, and out-of-order results must not attach to the wrong call or run.

## Review matrix

| Area | Verify | Failure patterns |
|---|---|---|
| Loop semantics | explicit progress, stop predicates, max steps, tool-call and token budgets | model alone decides when to stop |
| Tool dispatch | schema validation, call/result IDs, allowlist, result typing | transport success treated as business success |
| Side effects | stable idempotency key, atomic state, partial-effect reconciliation | retry creates a second charge or message |
| Context | deterministic ordering, provenance, truncation policy, authority separation | untrusted output promoted to system authority |
| State and memory | versioning, session and tenant keys, concurrency, retention | module-global memory crosses sessions |
| Concurrency | ownership, ordering, deduplication, locks or compare-and-set | two workers advance the same run |
| Failure handling | typed errors, bounded retry, backoff, timeout, degraded result | catch-all retry or false success |
| Cancellation | propagation to model, tools, queues, and checkpoints | UI says cancelled while work continues |
| Resume | checkpoint integrity and replay-safe effects | restart repeats an already committed effect |
| Maintainability | explicit interfaces, deterministic tests, documented invariants | policy scattered across prompt text |

## Required scenarios

Test a normal run plus malformed tool arguments, ambiguous timeout after an effect, duplicate result, late result after cancellation, process restart at a checkpoint, context limit pressure, and exhausted budget. Use inert adapters and deterministic clocks where possible.

Treat authority, correlation, isolation, idempotency, termination, and truthfulness as deterministic zero-tolerance invariants. Do not average one failure into task-quality results, and do not let high task success stand in for these checks.

## Findings

Name the violated invariant before proposing a pattern or library. Prefer the smallest enforceable fix: a state transition guard, stable idempotency key, independent authorization check, bounded counter, typed result schema, or explicit terminal reason.

Do not recommend a framework rewrite unless the evidence shows the current design cannot enforce the invariant.
