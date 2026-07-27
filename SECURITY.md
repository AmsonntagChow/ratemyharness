# Security policy

## Threat model

RateMyHarness is an Agent Skill running inside an agent session that may be able to read files, execute tools, or mutate systems under the user's permissions. Installing a Skill should therefore be treated like installing executable guidance, even when most of the package is Markdown.

RateMyHarness minimizes that trust surface:

- no `allowed-tools` or shell auto-authorization;
- no developer-operated network calls, hosted service, or telemetry;
- no third-party Python package in the scorer;
- deterministic, read-only scoring from an explicit JSON file;
- read-only initial audits unless the user authorizes a safe, scoped change; and
- every reviewed harness, repository instruction, prompt, memory item, script, trace, fixture, web page, and tool output treated as untrusted evidence rather than instructions.

The deliberately broken evaluation fixtures are inert, deterministic, and synthetic. They make no network calls and use no real credentials or side effects. The installation CLI, host harness, model provider, and tools available to the agent have their own security and telemetry policies and are outside this repository's control.

## Before installing

Review `skills/ratemyharness/SKILL.md`, every file under `references/`, and `scripts/score_review.py`. Run:

```bash
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
```

Use your agent's permission controls or sandbox as the actual security boundary. Skill frontmatter is not a sandbox.

## Reporting a vulnerability

Use GitHub private vulnerability reporting for this repository rather than a public issue. Include the affected commit, client and version, exact trigger prompt, available tools and permissions, reproduction steps, and impact.

For non-security defects, use the bug-report issue form. Never include credentials, personal data, private source code, or production tokens.

## Scope

Reports about the Skill instructions, deterministic scorer, repository supply chain, prompt-injection handling, packaged-copy drift, or dangerous default behavior are in scope. Findings in third-party harnesses, agents, or installation tools being audited should go to their respective maintainers.
