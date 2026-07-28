# Artifact-grounded oral defense

Use this route to test whether the author understands the actual harness. Score author understanding separately from independently verified runtime quality.

## Procedure

1. Complete the role and degree gate before inspecting the artifact.
2. Build an evidence inventory and identify a reachable runtime decision or failure.
3. Only then read the generator in `references/concept-probes.md`; do not load probe guidance at route selection.
4. Ask exactly one question and wait.
5. Score the answer, explain the missing consequence, and ask the next question.
6. Stop at the agreed count or when the user ends the defense.

Do not reveal the intended answer in the question. Prefer a concrete trace or failure sequence over definitions.

## Answer score

| Score | Meaning |
|---:|---|
| 0 | no answer or contradicts the artifact |
| 1 | names a term without the mechanism |
| 2 | explains the local mechanism but misses a material consequence |
| 3 | traces the failure end to end and proposes a sound control |
| 4 | also defines a falsifiable acceptance test and adjacent regression case |

Report two independent outputs:

- **Harness verdict** — based only on artifacts and runtime evidence.
- **Author understanding** — average answer score, strengths, and concepts to revisit.

Never lower a proven harness score because the author answers poorly, and never approve an unsafe harness because the author explains it well.
