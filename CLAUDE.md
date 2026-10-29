# rules-layer

AiDevelopProjects 下各项目共用的规则层源头。共享的规矩只住这里，各项目通过 `@` 引入、ruff `extend`、ESLint import 引用，不复制。

## 目录

- `rules/`：给 AI 与人读的规矩。`code-style.md`（九条）、`python.md`（Python 落法）、`workflow-gates.md`（三个检查点）、`copy-voice.md`（界面文案标准）。
- `lint/`：给工具读的基础配置。`ruff-base.toml`、`eslint-base.mjs`。
- `openspec-base/`：给项目照写的产物写法基础版 `artifact-rules.yaml`。
- `openspec/`：本仓库自己的 change。

## 不可违反的约定

- 每条规矩只住一处：共享的只放本仓库；项目专属的（红线、context、项目判断规则、回归用例）只放项目。
- 共享文件里不写任何项目的路径、命令或领域词。
- 改共享文件等于改所有接入项目：改之前先想清楚哪些项目受影响，改之后在受影响的项目验证。

## Code style

@rules/code-style.md
@rules/python.md

本仓库目前只有 Markdown、YAML 与两个 lint 配置文件，没有 Python 代码；引擎代码在 `judge-engine` change 中加入后再写样板路径。

## Workflow gates

@rules/workflow-gates.md

本项目命令表（在本仓库根目录执行）：

| 名称 | 命令 |
|---|---|
| 判断 | 判断层未装（`judge-engine` 完成前）。暂借章字书的 judge 只跑通用规则：在 `../zhangzishu/api` 下用 `uv run python -c` 调 `app.ai.judge` 的 `load_rules`、`lint_design`、`Judge.ask`，规则限 `proposal-states-non-goals`、`design-decisions-have-alternatives`、`design-no-speculative-extension` |
| ruff | 无 Python 代码，跳过 |
| 测试 | 无，跳过 |
| 前端 lint | 无前端，跳过 |
| 文案检查 | 无界面文案，跳过 |

红线规则：暂无（只有 `design-no-speculative-extension`）。

额外步骤：改了 `rules/` 或 `lint/` 时，在章字书与 Divination 各跑一次受影响的检查，确认结果与改前一致或差异已报告。

Notion 落点（启用阶段学习文档）：rules-layer 项目页 https://app.notion.com/p/408ebb79b33280158494d6bfb39b5bde ，编号子页「NN · 主题（要点 · 零基础）」。
