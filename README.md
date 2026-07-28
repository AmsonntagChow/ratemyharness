# RateMyHarness

English | [简体中文](README.zh-CN.md)

Evidence-backed release review for AI agent harnesses.

> Your agent completed a demo. Now prove the runtime deserves real tools, data, and users.

[![MIT License](https://img.shields.io/badge/license-MIT-2f855a.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-5b5bd6.svg)](https://agentskills.io/)

RateMyHarness audits the runtime around an AI agent: the loop, tool dispatch, context, state, memory, permissions, sandbox, approvals, retries, budgets, cancellation, termination, tracing, evaluation, and recovery.

## What it is

- The **model** proposes the next action.
- The **loop** repeatedly calls the model and tools.
- The **harness** contains that loop and enforces the surrounding runtime rules.
- A **Skill** shapes behavior inside a host harness; it cannot grant permissions or replace the sandbox.

So yes: the loop is part of the harness. RateMyHarness can review an isolated loop, but it labels that verdict as component-limited instead of pretending the whole runtime was audited.

## Installation

Choose one method. Do not install duplicate copies in the same client and scope.

For Codex, add this repository as a plugin marketplace:

```bash
codex plugin marketplace add AmsonntagChow/ratemyharness
```

Then open `/plugins` in Codex CLI or the Plugins Directory in the desktop app, install **RateMyHarness**, and start a new session. You can also run:

```bash
codex plugin add ratemyharness@ratemyharness
```

For Claude Code:

```text
/plugin marketplace add AmsonntagChow/ratemyharness
/plugin install ratemyharness@amsonntagchow-ratemyharness
/reload-plugins
```

For Cursor, Codex, Claude Code, or another Agent Skills client through the portable `skills` CLI:

```bash
npx skills add AmsonntagChow/ratemyharness --skill ratemyharness
```

The Skill can also be installed manually by copying `skills/ratemyharness` into the skills directory used by the agent.

## Start an audit

Give it a real harness repository, runtime folder, configuration, trace set, deployment, or runnable fixture. If the prompt does not already specify them, RateMyHarness first asks for two settings and waits:

```text
1. Role: Agent product owner / Staff agent-runtime engineer / Red-team reviewer / SRE/operator / Oral-defense professor
2. Review level: Quick check / Strict review / Release gate / Privileged review / Life-or-death review
```

It never silently defaults to the engineering role or the strictest review level. For example:

```text
As a Staff agent-runtime engineer, audit ./runtime for privileged production. Do not edit it or call external services. Give me the three fastest fixes.
```

| Role | Main judgment |
|---|---|
| Agent product owner | Does the harness improve task success enough to justify user effort, latency, and cost? |
| Staff agent-runtime engineer | Are loop, dispatch, state, context, concurrency, retry, and termination semantics correct? |
| Red-team reviewer | Can untrusted content, excess authority, secrets, memory, tools, or side effects make it unsafe? |
| SRE/operator | Can operators bound, observe, cancel, recover, roll out, and roll back the runtime? |
| Oral-defense professor | Does the author understand risks that actually exist in this artifact? |

Author understanding is scored separately. Weak answers do not erase verified runtime behavior, and a polished explanation does not make an unsafe harness safe.

## What it audits

1. Zero-tolerance deterministic runtime invariants: authority, correlation, isolation, idempotency, termination, and truthful state.
2. Probabilistic task quality: repeated success, unsafe outcomes, variance, latency, and cost per successful task.
3. Context ordering, provenance, truncation, persistent state, memory, and session isolation.
4. Timeouts, retry budgets, cancellation, checkpoints, resume, and deterministic termination.
5. Permissions, sandboxing, approvals, untrusted input, secrets, network, and tenant boundaries.
6. Queues, backpressure, tracing, incident recovery, and—only for public or higher targets—drift, canaries, and rollback.
7. Measurable task uplift over the simplest credible plain-loop or previous-runtime baseline.

It uses hard vetoes for authority bypass, cross-boundary data leakage, untrusted content controlling the runtime, runaway execution, duplicate irreversible effects, fabricated completion, unsafe code execution, hidden network behavior, broken core runtime paths, and license breaches. A good average cannot cancel one of those failures.

## Verdict

```text
Issue list:
- [H-002 · BLOCKER] Cancellation does not stop tool calls — the agent keeps spending money after the user presses Stop.
To verify:
- [U-003 · UNVERIFIED] Tenant isolation has not been exercised — one user's data may be exposed to another user.

Evidence lanes:
- deterministic-checks: FAIL
- critical-journey-e2e: PASS
- probabilistic-eval: UNVERIFIED
- continuous-evidence: N/A — local prototype has no deployment

Requested target:
Maximum safe target:
Decision: READY | READY WITH CONDITIONS | NOT READY | BLOCKED | INSUFFICIENT EVIDENCE
Harness score: optional
Runtime evidence:
Failure and recovery evidence:
Authority evidence:
Operational value:
Confidence:

Blockers:
Verified findings:
Unverified risks:
Top 3 actions:
Retest plan:
```

Every completed verdict starts with every verified issue, severity-sorted, as one plain-language line containing severity, failure, and consequence. Unverified items appear separately under `To verify`; fixes, evidence, and technical detail stay below, and only the next-action list is capped at three.

The four evidence lanes are independent and use only `PASS`, `FAIL`, `UNVERIFIED`, or `N/A`. Every evidence item declares its lane and assertion type, so a structural repository test cannot masquerade as a critical E2E run. Deterministic checks cannot hide poor task success, and a strong model cannot hide a broken runtime. Probabilistic evidence records equal-arm successes, count-derived uplift, thresholds, bounded variance, cost per success, latency, and the exact harness/build, model, prompt, tool-schema, retrieval/data, dataset, rubric, and judge identity. Every judge has a kind, ID, version, and digest; an LLM judge also needs calibration.

Every finding includes exact reproduction, expected and actual behavior, evidence strength, impact, the smallest safe fix, an acceptance test, and a neighboring regression case.

## Why this is not another code reviewer

A code reviewer can find local bugs. RateMyHarness follows runtime invariants across components: approval to dispatch, tool call to result, retry to external effect, session to memory, cancellation to cleanup, checkpoint to resume, and trace to terminal claim.

A valid configuration or green repository CI proves structure, not real harness behavior. Public or privileged approval requires fresh critical-journey runs, deterministic failure injection, repeated quality evals, deploy evidence, authority tests, continuous signals, and a comparison with a simpler baseline.

## Scoring

The optional scorer is deterministic and uses only the Python standard library:

```bash
python3 skills/ratemyharness/scripts/score_review.py --pretty evals/scorecards/blocked-release.json
```

It validates evidence links and weights, enforces target-specific non-substitutable lanes, recomputes task success and uplift from equal-arm counts, gates excessive variance, verifies judge identity, and binds probabilistic and continuous evidence to one identity SHA-256. An active gate may optionally list exact `affected_targets`: omitting the field preserves the legacy all-target block, while output separates all `active_gates` from the `blocking_gates` that affect the requested target.

Scorecard schema v2 is a fail-closed migration. Existing v1 scorecards must add each evidence item's `lane` and `assertion_type`, the complete four-lane panel, and `quality_evaluation`; old evidence must not be relabeled fresh without rerunning it.

## Trust and safety

The first audit is read-only. RateMyHarness does not grant tools, deploy services, install dependencies, weaken sandboxes, read credentials, send telemetry, or call real external systems. Its fixtures use synthetic values and in-memory effects.

RateMyHarness is itself only a Skill running inside the host harness. The host's sandbox, permissions, and approval system remain the real security boundary. See [SECURITY.md](SECURITY.md), [PRIVACY.md](PRIVACY.md), and [TERMS.md](TERMS.md).

## Repository layout

```text
.claude-plugin/              Claude Code plugin and marketplace manifests
.agents/plugins/             Codex repository marketplace
plugins/ratemyharness/       self-contained universal plugin and listing assets
skills/ratemyharness/        canonical portable Skill, references, UI metadata, scorer
evals/trigger_cases.json     positive and near-miss selection evals
evals/execution_cases.json   with-Skill versus without-Skill behavior evals
evals/fixtures/              safe synthetic runtime failure cases
submission/                  public directory listing copy and review tests
scripts/                     package synchronization and repository validation
tests/                       deterministic scorer tests
```

## Development

```bash
python3 scripts/sync_codex_plugin.py --check
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
claude plugin validate . --strict
python3 /path/to/plugin-creator/scripts/validate_plugin.py plugins/ratemyharness
```

These commands validate repository structure, fixtures, and scorer behavior; a green result is not evidence that RateMyHarness or an audited harness performed well in a real model run. Contributions must include captured behavioral evidence, not only a prose diff. Read [CONTRIBUTING.md](CONTRIBUTING.md).

This repository's authoring approach is informed by [Building a High-Quality Agent Skill from Scratch and Running It as an Open-Source Project](https://research.xishe.ai/skill-authoring-and-oss), especially its guidance on description-first discovery, progressive disclosure, separated trigger and execution evals, reference integrity, zero-dependency scripts, and open-source distribution.

## License

[MIT](LICENSE) © 2026 AmsonntagChow
