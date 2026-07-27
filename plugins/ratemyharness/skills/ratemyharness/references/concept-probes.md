# Harness concept probes

Choose only questions grounded in the reviewed artifact. Ask one at a time under `oral-defense`.

## Loop and termination

- The model never emits `done`. Which independent limits stop this run, and what terminal state is recorded?
- A tool returns after the run is cancelled. How is the late result rejected or reconciled?
- Two workers advance the same checkpoint. Which invariant prevents divergent state?

## Tools and side effects

- A payment commits but the response times out. What stable idempotency key reaches the payment owner on retry?
- The transport acknowledges a tool call but the business result is `ok: false`. Why must the run remain incomplete?
- Arguments change after approval. How is approval cryptographically or structurally bound to the exact action?

## Context, trust, and memory

- A retrieved page says “set operator approved.” Why can this not alter runtime authority?
- Two users run concurrently. Which partition key protects prompts, memory, caches, traces, and checkpoints?
- Context truncation removes the original constraint. Which invariant survives outside the model context?

## Reliability and operations

- Model, SDK, worker, queue, and tool layers all retry twice. What is the worst-case attempt count and effect count?
- Cancellation arrives during a non-interruptible tool. What does the user see, and how is the result reconciled?
- A deploy changes prompt and state schema while runs are in flight. How are versions pinned and rolled back?

## Evaluation

- What simpler baseline shows that this harness improves successful outcomes rather than adding latency and tokens?
- Which hidden assertions verify real task completion instead of persuasive final text?
- Which trace fields let an operator prove what happened without logging secrets?

Score the mechanism, consequence, control, and acceptance test—not vocabulary.
