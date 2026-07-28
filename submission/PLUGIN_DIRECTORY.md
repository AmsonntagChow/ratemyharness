# OpenAI Plugins Directory submission

Use this sheet with the [OpenAI plugin submission portal](https://platform.openai.com/plugins). Choose **Skills only** and upload `dist/ratemyharness-plugin-1.0.1.zip`.

The public directory is universal: one approved listing can appear in ChatGPT and Codex. Public availability begins only after OpenAI review and the publisher's separate **Publish** action.

## Listing

- **Plugin name:** RateMyHarness
- **Short description:** Audit agent harnesses safely
- **Category:** Developer Tools
- **Developer:** AmsonntagChow
- **Website:** https://github.com/AmsonntagChow/ratemyharness
- **Support:** https://github.com/AmsonntagChow/ratemyharness/issues
- **Privacy:** https://github.com/AmsonntagChow/ratemyharness/blob/main/PRIVACY.md
- **Terms:** https://github.com/AmsonntagChow/ratemyharness/blob/main/TERMS.md
- **Logo and composer icon:** `plugins/ratemyharness/assets/logo.png`

**Long description**

RateMyHarness audits the runtime around an AI agent, not just its prompt or loop. Choose a harness owner, Staff agent-runtime engineer, red-team reviewer, SRE/operator, or oral-defense professor, then choose how hard to judge it. The plugin traces model and tool turns; checks context and state isolation, permissions, side effects, retries, budgets, cancellation, termination, recovery, observability, and eval evidence; blocks unsafe releases; and returns reproducible findings, the three fastest fixes, and a same-rubric retest plan.

## Starter prompts

1. As a Staff agent-runtime engineer, audit this harness for public release and give me the three fastest fixes.
2. Red-team this agent harness at privileged depth. Find authority, isolation, tool, and side-effect failures.
3. As an SRE, test this harness for runaway loops, retries, cancellation, recovery, cost, and observability.

## Review tests

Enter the five positive and three negative cases from `submission/plugin-test-cases.json`. Every positive fixture is public and synthetic and requires no account, credential, private network, external service, or destructive execution.

## Release notes

Version 1.0.1 update. Adds a severity-sorted one-line issue index and four non-substitutable evidence lanes; separates deterministic runtime invariants from repeated task quality; requires equal-arm baseline uplift, bounded variance, versioned judge identity, and a shared evaluation/deployment digest; scopes gates to affected targets; and migrates optional scorecards to fail-closed schema v2.

## Package contents

The ZIP contains exactly one plugin root:

```text
.codex-plugin/plugin.json
assets/logo.png
assets/logo.svg
skills/ratemyharness/SKILL.md
skills/ratemyharness/agents/openai.yaml
skills/ratemyharness/references/*.md
skills/ratemyharness/scripts/score_review.py
```

It deliberately excludes repository marketplaces, `.git`, README files, tests, fixtures, screenshots, MCP configuration, and app configuration.

## Before submitting

- Select the verified individual or business identity matching `AmsonntagChow` and confirm Apps Management write access.
- Upload the final ZIP and square logo, then paste the three starter prompts and eight review tests.
- Choose only countries or regions where the plugin can be supported.
- Complete release notes and policy attestations, then submit for review.
- Wait for security scanning and review. Approval does not publish automatically; return to the portal and choose **Publish**.
