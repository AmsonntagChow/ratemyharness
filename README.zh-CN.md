# RateMyHarness

[English](README.md) | 简体中文

为 AI Agent 运行底座提供基于证据的上线评审。

> 你的 Agent 已经完成了演示。现在，请证明这套运行时值得接入真实的工具、数据和用户。

[![MIT License](https://img.shields.io/badge/license-MIT-2f855a.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-5b5bd6.svg)](https://agentskills.io/)
[![ratemy.sh](https://img.shields.io/badge/ratemy.sh-harness-C4500F.svg)](https://harness.ratemy.sh/zh/)
[![skills.sh](https://skills.sh/b/AmsonntagChow/ratemyharness)](https://skills.sh/amsonntagchow/ratemyharness/ratemyharness)

RateMyHarness 审计 AI Agent 周边的运行时：循环、工具分发、上下文、状态、记忆、权限、沙箱、审批、重试、预算、取消、终止、追踪、评估和恢复。

## 它是什么

- **模型**提出下一步操作。
- **循环**反复调用模型和工具。
- **Harness（运行底座）**包含这个循环，并执行周边的运行时规则。
- **Skill** 在宿主 Harness 内塑造行为；它无法授予权限，也不能取代沙箱。

所以没错：循环是 Harness 的一部分。RateMyHarness 可以评审一个独立的循环，但它会把结论标记为仅限组件，而不会假装整个运行时都已经接受过审计。

## 安装

请选择一种方式。不要在同一个客户端和作用域中安装重复副本。

`skills` CLI 最短，且在 Codex、Claude Code、Cursor 以及其他所有 Agent Skills 客户端都能用：

```bash
npx skills add AmsonntagChow/ratemyharness --skill ratemyharness
```

对于 Codex，请将此仓库添加为插件市场：

```bash
codex plugin marketplace add AmsonntagChow/ratemyharness
```

然后在 Codex CLI 中打开 `/plugins`，或在桌面应用中打开 Plugins Directory，安装 **RateMyHarness** 并启动新会话。或者直接跑这两条命令：

```bash
codex plugin add ratemyharness@amsonntagchow-ratemyharness
```

对于 Claude Code：

```text
/plugin marketplace add AmsonntagChow/ratemyharness
```

只发这一条：`/plugin` 会把它后面的全部内容当作一个参数，多行粘贴会被读成一个畸形仓库名。添加成功后打开 `/plugins`，在菜单里安装 **RateMyHarness**，再开一个新会话。

也可以手动安装此 Skill：将 `skills/ratemyharness` 复制到 Agent 使用的 Skill 目录中。 所有方式都不会自动更新：要升级到新版本，重新执行一次安装命令即可。

## 开始审计

请向它提供真实的 Harness 仓库、运行时文件夹、配置、追踪记录集、部署或可运行的测试夹具。如果提示词尚未指定以下设置，RateMyHarness 会先询问两个问题并等待回答：

```text
1. 角色：Agent 产品负责人 / Staff Agent Runtime 工程师 / 红队审查员 / SRE 运行负责人 / 答辩老师
2. 程度：快速体检 / 严格评审 / 上线门禁 / 特权审查 / 生死审查
```

它绝不会在未告知你的情况下默认采用工程师角色或最严苛的程度。例如：

```text
以 Staff Agent Runtime 工程师的身份，针对特权生产环境审计 ./runtime。不要编辑它，也不要调用外部服务。给我三个见效最快的修复建议。
```

| 角色 | 核心判断 |
|---|---|
| Agent 产品负责人 | Harness 对任务成功率的提升，是否足以抵消用户投入、延迟和成本？ |
| Staff Agent Runtime 工程师 | 循环、分发、状态、上下文、并发、重试和终止语义是否正确？ |
| 红队审查员 | 不受信任的内容、过度授权、密钥、记忆、工具或副作用是否会使其变得不安全？ |
| SRE/运行负责人 | 运维人员能否限制、观测、取消和恢复运行时，并进行发布和回滚？ |
| 答辩老师 | 作者是否理解这个项目产物中实际存在的风险？ |

作者理解程度会单独评分。薄弱的回答不会抹去已经验证的运行时行为，出色的解释也不能让不安全的 Harness 变安全。

## 审计内容

1. 零容忍的确定性运行时不变量：授权约束、关联、隔离、幂等性、终止和状态真实性。
2. 概率性任务质量：重复成功、不安全结果、方差、延迟和每次成功任务的成本。
3. 上下文顺序、来源可追溯性、截断、持久状态、记忆和会话隔离。
4. 超时、重试预算、取消、检查点、恢复执行和确定性终止。
5. 权限、沙箱、审批、不受信任的输入、密钥、网络和租户边界。
6. 队列、背压、追踪、事故恢复，以及仅适用于公开级或更高等级目标的漂移、金丝雀发布和回滚。
7. 相较于最简单且可信的普通循环或上一版运行时基线，可衡量的任务提升。

对于授权绕过、跨边界数据泄露、不受信任内容控制运行时、失控执行、重复产生不可逆副作用、伪造完成状态、不安全的代码执行、隐藏的网络行为、核心运行路径损坏和许可证违规，它采用硬性否决。一项良好的平均分无法抵消其中任何一项失败。

## 结论

```text
问题清单：
- [H-002 · BLOCKER] 取消操作未能停止工具调用——用户按下“停止”后，Agent 仍在继续产生费用。
待验证：
- [U-003 · UNVERIFIED] 尚未演练租户隔离——一名用户的数据可能暴露给另一名用户。

证据通道：
- deterministic-checks: FAIL
- critical-journey-e2e: PASS
- probabilistic-eval: UNVERIFIED
- continuous-evidence: N/A — 本地原型没有部署

请求目标：
最高安全目标：
决策：READY | READY WITH CONDITIONS | NOT READY | BLOCKED | INSUFFICIENT EVIDENCE
Harness 评分：可选
运行时证据：
失败与恢复证据：
授权证据：
运维价值：
置信度：

阻断项：
已验证发现：
未验证风险：
前三项行动：
复测计划：
```

每个完整结论开头都会列出所有已验证问题，并按严重程度排序；每个问题以一行直白语言说明严重程度、故障及其后果。未验证项单独列在`待验证`下；修复方案、证据和技术细节置于下方，仅后续行动清单以三项为上限。

四条证据通道彼此独立，并且只使用 `PASS`、`FAIL`、`UNVERIFIED` 或 `N/A`。每项证据都声明所属通道和断言类型，因此结构性仓库测试无法冒充关键流程端到端运行。确定性检查不能掩盖低劣的任务成功率，强大的模型也不能掩盖损坏的运行时。概率性证据会记录各等量分组的成功次数、由计数得出的提升、阈值、有界方差、每次成功的成本、延迟，以及确切的 Harness/构建、模型、提示词、工具 schema、检索/数据、数据集、评分标准和评判器身份。每个评判器都有 kind、ID、version 和 digest；LLM 评判器还需要校准。

每项发现都包括精确复现步骤、预期行为与实际行为、证据强度、影响、最小安全修复、验收测试和相邻回归用例。

## 为什么这不是又一个代码审查工具

代码审查工具可以发现局部缺陷。RateMyHarness 则会跨组件追踪运行时不变量：从审批到分发、从工具调用到结果、从重试到外部副作用、从会话到记忆、从取消到清理、从检查点到恢复执行，以及从追踪记录到终态声明。

有效的配置或全绿的仓库 CI 只能证明结构，不能证明真实的 Harness 行为。要批准公开级或特权级目标，需要新近完成的关键流程运行、确定性故障注入、重复质量评估、部署证据、授权测试、持续信号，以及与更简单基线的对比。

## 评分

可选评分器是确定性的，并且只使用 Python 标准库：

```bash
python3 skills/ratemyharness/scripts/score_review.py --pretty evals/scorecards/blocked-release.json
```

它会验证证据链接和权重、执行特定目标下不可替代的通道要求、根据等组计数重新计算任务成功率和提升、拦截过高方差、验证评判器身份，并将概率性证据和持续证据绑定到同一个身份 SHA-256。启用的门禁可以选择列出确切的 `affected_targets`：省略该字段会保留旧版的全目标阻断行为，而输出则会把所有 `active_gates` 与影响请求目标的 `blocking_gates` 分开显示。

记分卡 schema v2 的迁移采用失败时默认拒绝（fail-closed）策略。现有 v1 记分卡必须为每个证据项添加 `lane` 和 `assertion_type`、完整的四通道面板以及 `quality_evaluation`；旧证据未经重新运行，不得重新标记为最新证据。

## 信任与安全

首次审计是只读的。RateMyHarness 不会授予工具访问权、部署服务、安装依赖、削弱沙箱、读取凭据、发送遥测数据或调用真实的外部系统。它的测试夹具使用合成值和仅发生在内存中的副作用。

RateMyHarness 本身只是一个运行在宿主 Harness 内的 Skill。宿主的沙箱、权限和审批系统仍然是真正的安全边界。请参阅 [SECURITY.md](SECURITY.md)、[PRIVACY.md](PRIVACY.md) 和 [TERMS.md](TERMS.md)。

## 仓库结构

```text
.claude-plugin/              Claude Code 插件和市场清单
.agents/plugins/             Codex 仓库市场
plugins/ratemyharness/       自包含的通用插件及上架素材
skills/ratemyharness/        规范的可移植 Skill、参考资料、UI 元数据和评分器
evals/trigger_cases.json     正向及相似非目标选择评测
evals/execution_cases.json   使用 Skill 与不使用 Skill 的行为评测
evals/fixtures/              安全的合成运行时故障用例
submission/                  公开目录上架文案和评审测试
scripts/                     软件包同步和仓库验证
tests/                       确定性评分器测试
```

## 开发

```bash
python3 scripts/sync_codex_plugin.py --check
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
claude plugin validate . --strict
python3 /path/to/plugin-creator/scripts/validate_plugin.py plugins/ratemyharness
```

这些命令会验证仓库结构、夹具和评分器行为；结果全绿并不能证明 RateMyHarness 或被审计的 Harness 在真实模型运行中表现良好。贡献必须包含已捕获的行为证据，而不能只有文字差异。请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

本仓库的编写方式参考了[《从零做一个高质量 Agent Skill，并把它当开源项目运营》](https://research.xishe.ai/skill-authoring-and-oss)，尤其是其中关于描述优先的发现机制、渐进式披露、触发评估与执行评估分离、引用完整性、零依赖脚本和开源分发的指导。

## 许可证

[MIT](LICENSE) © 2026 AmsonntagChow
