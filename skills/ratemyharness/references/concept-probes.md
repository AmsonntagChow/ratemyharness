# Artifact-grounded probe generator

Read this only after the reviewed harness has supplied a concrete runtime decision, trace transition, or reachable failure. Generate one question at a time; do not select from a fixed question bank.

## Probe interface

Construct each question from four artifact-specific inputs:

| Input | Requirement |
|---|---|
| `evidence_anchor` | Name an exact function, config field, trace event, state transition, tool boundary, or observed result. |
| `decision_under_test` | Identify the author's choice about authority, correlation, stopping, retries, effects, isolation, recovery, operations, or evaluation. |
| `counterfactual` | Change one condition with a plausible failure: timeout, cancellation, duplicate or late result, restart, concurrency, hostile content, exhausted budget, or version change. |
| `proof_bar` | Ask for the mechanism, consequence, enforcing control, and falsifiable acceptance test. |

Render a single concise scenario question that contains the evidence anchor and counterfactual without revealing the expected answer. Match the user's language and vocabulary.

## Selection rule

Choose the decision with the highest combination of reachable consequence and uncertainty in the current artifact. Prefer a boundary that the available evidence can actually illuminate. Do not ask definitions, generic best-practice trivia, or a scenario unsupported by the artifact.

After each answer, use the oral-defense rubric to score mechanism, consequence, control, and verification. Generate a follow-up only when one missing link would distinguish real understanding from memorized vocabulary; otherwise move to a different evidenced decision or stop at the agreed count.
