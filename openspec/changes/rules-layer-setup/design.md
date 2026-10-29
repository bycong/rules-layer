# Design

## Context

动机见 proposal.md，要求见 `specs/rules-layer-setup`。影响做法的现状：

- 共享部分都已就位：`rules/` 四份规矩、`lint/` 两份基础配置、`openspec-base/artifact-rules.yaml`、`judge/` 引擎（`v0.3.1`），引擎自带三条通用规则与通用词表。
- 两个已接入项目的落法可作参照：章字书（uv、`api/` 后端、React 前端、无 CI）、Divination（venv 由 uv 建、`backend/`、单文件前端、有 CI 钉 rules-layer 版本）。
- 试跑对象 boyangcong：Python 脚本与表单服务（`bycong/scripts`、`bycong/form` 带 `requirements.txt` 与 `.venv`），无 `pyproject.toml`、无 ruff 配置、无 CI；`openspec/config.yaml` 有 context 无 rules；已归档 5 个 change；工作区有用户 28 个未提交改动。
- Claude Code 的 skill 是目录里的 `SKILL.md`（frontmatter 写 `name` 与 `description`）加任意辅助文件；放在 `~/.claude/skills/<名>/` 即全局可用。

## Goals / Non-Goals

**Goals:**
- 识别与巡检的结论可重复、可测试，不随 AI 每次查法不同而变。
- 先在已接入项目只读验证，再动 boyangcong。

**Non-Goals:**
- 不做插件打包、不做自动安装脚本。
- 不给其他项目（Klarpix、Slidewand、yybu 等）接入。

## Decisions

### 1. 识别与巡检由脚本 `check.py` 产出，`SKILL.md` 负责判断与动手

`skills/rules-layer/check.py` 只读：输出识别表（语言、包管理、目录、openspec、归档数、CI 与钉的版本、未提交改动、各层状态）与巡检各项结果，纯文本。`SKILL.md` 让 AI 先运行它，再按结果决定做哪一阶段、向用户提问、写文件。脚本用 `uv run --script` 运行，依赖写在文件头（只需 pyyaml），有自己的测试。

- 被否决：全写在 `SKILL.md` 里由 AI 每次自己 grep。省一个文件，但每次查法可能不同，结论无法测试；巡检的价值在于稳定。
- 被否决：脚本也负责写文件。阶段一、三要问用户、要按项目调整措辞，交给 AI 更合适；脚本只做确定性的读与比对。

### 2. 模板放 `skills/rules-layer/templates/`

`CLAUDE.md` 骨架、`ruff.toml`、`judge.yaml`、`judgments.yaml` 骨架、`judge_cases.yaml` 骨架各一份，内容只含结构与占位说明，不含任何项目的规则或红线。产物写法不另做模板，直接取 `openspec-base/artifact-rules.yaml`。

- 被否决：模板写在 `SKILL.md` 正文。文件过长，AI 读时容易漏步骤。

### 3. 没有 `pyproject.toml` 的项目在根目录放 `ruff.toml`

`ruff.toml` 写 `extend = "../rules-layer/lint/ruff-base.toml"` 与按需的豁免。已有 `pyproject.toml` 的项目写进它的 `[tool.ruff]`。

- 被否决：为放 ruff 配置新建 `pyproject.toml`。boyangcong 没有要管理的包，新建它只会让人误以为这是个 Python 包。

### 4. 安装是一条软链接，写进本仓库 README

`ln -s ~/AiDevelopProjects/rules-layer/skills/rules-layer ~/.claude/skills/rules-layer`。本仓库新建 `README.md`，写明目录、安装 skill、安装 `jev-judge`、配置 key、启用提交前钩子。

- 被否决：打包成 Claude Code 插件。一个人用，插件的发布与更新流程比一行命令重。

### 5. 巡检只报真正的偏离：基础条目缺失或改写、内容完全相同的重复

项目在共享基础之上的追加与有意覆盖都是规格允许的，巡检不报；只报会让项目和共享版本对不上的情况。各项的具体比对方法见下文「巡检比对方法」。

- 被否决：产物写法要求项目 `rules` 与基础版整段一字不差。Divination 在 Risks 那条后追加了兼容旧写法的说明，属于规格允许的追加，整段比对会把它误报成差异。
- 被否决：重复规则按 id 判断，同 id 一律报。项目用同 id 收紧通用规则是规格允许的覆盖，只有内容也完全相同才是多余副本。
- 被否决：巡检时顺手修正。巡检常在有未提交改动的项目里跑，自动改容易和用户的改动缠在一起；规格已要求只报告。

### 6. 试跑顺序：先只读，后写

先在章字书、Divination 跑巡检，核对脚本结论与人工核对一致；再在 boyangcong 跑阶段一。boyangcong 的红线候选取自其 `config.yaml` context（无注册/登录/UGC、产品仅图文展示与外链、表单最小采集等），逐条由用户确认。

- 被否决：先跑 boyangcong。它有用户 28 个未提交改动，脚本若有误，那里代价最大。

## 巡检比对方法

- 引入：`CLAUDE.md` 有 `## Code style`、`## Workflow gates` 两个标题，且其下有 `@../rules-layer/rules/` 引入。
- 产物写法：基础版每一条都在项目 `rules` 的对应产物下且一字不差；项目多出的条目视为追加，不报。
- lint：ruff 配置有 `extend` 指向 `ruff-base.toml` 且没有 `select`；有 ESLint 配置时 import 了 `eslint-base.mjs`。
- 引擎副本：项目里出现定义了 `def load_rules` 且路径不在 rules-layer 的 `.py` 文件。
- 重复规则：项目 `judgments.yaml` 中与引擎通用规则同 id 且内容完全相同的条目（同 id 但不同是有意覆盖，不报）。
- 词表：项目词表中已在通用词表的词。
- CI：工作流里 `repository: bycong/rules-layer` 的 `ref` 早于本仓库最新 tag 时报告，并列出两版本间改动的共享文件。

## Risks / Trade-offs

- [`SKILL.md` 指令被 AI 执行时跳步] → 步骤编号、每步写明「做完的标志」；脚本输出的下一阶段写在最后一行，AI 照它走
- [巡检比对规则太严，把有意的项目差异报成问题] → 产物写法只报基础条目缺失或改写；同 id 不同内容视为有意覆盖
- [boyangcong 新增 `CLAUDE.md` 立即影响该项目的所有会话] → 汇报中提醒；需要时删除该文件即恢复
- [外部引入未同意导致 `CLAUDE.md` 引入不生效] → 汇报提醒在交互会话同意一次，并给出验证问法

## Migration Plan

1. 本仓库：写 `check.py` 与测试、`SKILL.md`、模板、`README.md`；建软链接；提交并打 tag。
2. 只读试跑：章字书、Divination 巡检，结论与人工核对对比，差异修脚本。
3. boyangcong：跑阶段一，用户确认红线后写文件；验证；不提交，由用户决定。
4. Notion 搭建手册开头加指向 `/rules-layer` 的说明。

回滚：删除软链接即停用 skill；boyangcong 的阶段一产物未提交，删除新文件、`git checkout openspec/config.yaml` 即恢复。

## 改动文件与估计行数

| 位置 | 文件 | 估计 |
|---|---|---|
| rules-layer | `skills/rules-layer/SKILL.md` | +120 |
| | `skills/rules-layer/check.py` | +220 |
| | `skills/rules-layer/tests/test_check.py` | +150 |
| | `skills/rules-layer/templates/`（5 个文件） | +80 |
| | `README.md` | +40 |
| boyangcong（不提交） | `CLAUDE.md` | +50 |
| | `ruff.toml` | +6 |
| | `openspec/config.yaml` | +15 |
