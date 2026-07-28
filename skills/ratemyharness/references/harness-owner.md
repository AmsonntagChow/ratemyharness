# Agent product owner and harness-user review

Use this route to answer whether the harness makes a real workflow better for its users. Do not substitute framework sophistication for user value.

## Contract

Write a one-sentence contract before testing:

```text
For <user>, the harness turns <input> into <observable outcome> within <time/cost/control limits>, and fails by <safe behavior>.
```

Name the simplest credible baseline: a plain model call, a bounded tool loop, the previous runtime, or a human workflow. Compare the same model, tools, data, permissions, and stopping condition.

Keep runtime correctness and task quality separate. A stable harness with poor task success is not a good product; a capable model running inside a harness that leaks data or duplicates effects is not a safe product.

## Review matrix

| Question | Strong evidence | Common failure |
|---|---|---|
| Does the task finish correctly? | repeated task-level assertions and verified external state | fluent final text despite a failed tool |
| Does the harness add value? | with-harness uplift over the simplest baseline | architecture exists but outcome is unchanged |
| Is user effort lower? | fewer clarifications, retries, and manual repairs | agent shifts orchestration work to the user |
| Can the user control it? | visible plan, bounded scope, approval and cancel behavior | unclear authority or ignored cancellation |
| Is latency acceptable? | end-to-end percentiles and slow-path traces | average model latency only |
| Is cost acceptable? | tokens, tool calls, retries, and infrastructure per successful task | cost per request without success denominator |
| Does failure remain useful? | accurate partial result, recovery path, and preserved state | silent retry loop or false success |
| Is repeated use trustworthy? | session isolation and stable behavior across runs | stale memory changes unrelated users or tasks |

## Minimum tests

1. Run at least one representative happy path and verify the real outcome, not only the final answer.
2. Inject one tool failure and one cancellation; verify truthful reporting and cleanup.
3. Compare repeated runs against the simplest baseline using hidden task assertions and one immutable harness/model/prompt/tools/data/dataset/rubric/judge identity tuple.
4. Record thresholds, success variance, user interventions, latency, cost per successful task, and unsafe effects; calibrate any LLM judge.
5. Test one repeated run to reveal stale state or duplicate side effects.

## Product verdict rules

- Valid code without measured workflow improvement is `NOT READY` for a product claim.
- A narrow harness that reliably solves one job can outrank a general autonomous agent.
- Missing baseline evidence is `INSUFFICIENT EVIDENCE`, not proof that the harness has no value.
- Treat user acceptance of risk as a product choice, not as a technical safety pass.

Return the three changes most likely to improve successful outcomes per unit of user effort, latency, and cost.
