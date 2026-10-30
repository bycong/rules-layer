# rules-layer-setup Specification

## Purpose
规定 `/rules-layer` skill 在任一项目根目录运行时如何识别项目、判断已装到哪一层、补上下一层，以及对已装好的项目只做巡检，使新项目接入规则层不再照手册手抄，已接入项目能发现自己与共享版本的差距。

## Requirements

### Requirement: skill 只住本仓库，任何项目可用

skill 的说明与模板 SHALL 只在本仓库 `skills/rules-layer/` 一份，`~/.claude/skills/rules-layer` 是指向它的软链接，在任一项目根目录都能调用。skill MUST NOT 被复制进项目。

#### Scenario: 修改 skill
- **WHEN** skill 的某一步需要调整
- **THEN** 只改本仓库 `skills/rules-layer/`，所有项目下次调用即用上新版本

### Requirement: 先识别项目再做事

每次运行 SHALL 先输出一张识别表：语言与包管理（uv / pip / pnpm / npm）、后端与前端目录及前端形态、有无 openspec、已归档 change 数、有无 CI 及 CI 钉的 rules-layer 版本、工作区是否有未提交改动、各层安装状态。不在 git 仓库或没有 `openspec/` 时 MUST 停下，说明需先 `openspec init`，不做其他改动。

#### Scenario: boyangcong
- **WHEN** 在 boyangcong 根目录运行
- **THEN** 识别表显示 Python（`bycong/scripts`、`bycong/form`）、无前端构建、有 openspec、已归档 5 个、无 CI、有未提交改动、各层均未安装

#### Scenario: 没有 openspec
- **WHEN** 在一个没有 `openspec/` 的仓库运行
- **THEN** 只输出识别表与「先运行 openspec init」，不写任何文件

### Requirement: 按安装状态而非归档数决定下一步

skill SHALL 按「阶段一 → 阶段二 → 阶段三 → 巡检」的顺序找出第一个未完成的阶段，每次运行只做这一个阶段；归档数只决定判断层能否安装，不决定从哪一阶段开始。做之前 MUST 列出将新增与修改的文件，等用户确认后才写。

#### Scenario: 历史多但未接入
- **WHEN** 项目已归档 5 个 change，但没有 `CLAUDE.md`
- **THEN** 本次只做阶段一，不跳到阶段三

#### Scenario: 用户未确认
- **WHEN** skill 列出将改动的文件后用户没有同意
- **THEN** 不写任何文件，汇报停在识别与计划

### Requirement: 阶段一接入代码规矩与 gates

阶段一 SHALL 产出：`CLAUDE.md`（项目简介、红线小节、`## Code style` 与 `## Workflow gates` 两个标题下的 `@../rules-layer/...` 引入、本项目命令表）；`openspec/config.yaml` 的 `rules` 段照共享产物写法基础版写入；ruff 与 ESLint 配置继承共享基础规则（按项目实际语言，没有的不建）。此时判断层未装，命令表中判断与文案检查写明「判断层未装」。

#### Scenario: Python 项目没有 ruff 配置
- **WHEN** 项目有 Python 代码但没有任何 ruff 配置
- **THEN** 新建一份只含 `extend` 与按需豁免的配置，运行 ruff 后把报出的问题列进汇报，不自动修代码

#### Scenario: 已有 config.yaml context
- **WHEN** 项目 `openspec/config.yaml` 已有 `context` 段
- **THEN** 保留原 `context`，只补 `rules` 段

### Requirement: 红线由人确认，skill 不代写

skill 提出的红线与判断规则候选 SHALL 注明出处（项目 README、`openspec/config.yaml` 的 `context`、或某个已归档方案），写入 `CLAUDE.md` 红线小节或 `judgments.yaml` 前 MUST 逐条请用户确认或改写；用户没有确认的候选 MUST NOT 写入。

#### Scenario: 从 context 提候选
- **WHEN** boyangcong 的 `config.yaml` context 写着「无注册/登录/UGC」
- **THEN** skill 把它列为红线候选，等用户确认后才写进 `CLAUDE.md`

### Requirement: 阶段二整理候选判断规则

阶段一完成、判断层未装时，SHALL 读已归档 change 的 proposal 与 design，整理反复出现、且能指回已写下规矩的问题，作为候选判断规则列在汇报里（规则 id、要问的一句话、enforces 指向哪条规矩、出现在哪几个 change）。已归档不足 3 个时 MUST 说明还不能装判断层，并在汇报里写明还差几个。

#### Scenario: 归档不足
- **WHEN** 项目只归档了 2 个 change
- **THEN** 汇报写明「判断层需至少 3 个已归档 change 作测试用例，还差 1 个」，不生成 `judgments.yaml`

### Requirement: 阶段三安装判断层

已归档至少 3 个 change、且用户确认了至少一条项目判断规则时，SHALL 产出：只含用户确认规则的 `openspec/judgments.yaml`（通用三条由引擎自带，不写入）；`openspec/judge.yaml`（项目有界面文案才写 `copy` 段）；`tests/judge_cases.yaml` 骨架；命令表的判断与文案检查改为 `jev-judge`。缺 `jev-judge` 命令或 `~/.config/jev-judge/env` 时 MUST 给出安装与配置步骤，不代填 key。

#### Scenario: 没有 key
- **WHEN** 本机没有 `~/.config/jev-judge/env`
- **THEN** 汇报给出创建该文件的步骤，判断层文件照常生成，`jev-judge` 以人工模式运行验证

### Requirement: 已装好的项目只巡检、不改文件

各阶段都已完成的项目，skill SHALL 只读检查并报告：`@` 引入是否缺失；`config.yaml` 的 `rules` 与共享基础版的差异（基础条目缺失或改写才报，追加不报）；ruff 或 ESLint 配置仍写 `select` 或未继承；项目里是否留有判断引擎副本；项目规则中与通用规则同 id 且内容相同的多余副本；项目词表中已在通用词表的词；CI 钉的 rules-layer 版本是否落后于最新 tag。巡检 MUST NOT 修改任何文件。

#### Scenario: 章字书巡检
- **WHEN** 在章字书运行
- **THEN** 输出各项检查结果；没有差异的项写「一致」，有差异的列出文件与内容；工作区不出现任何改动

#### Scenario: CI 版本落后
- **WHEN** Divination 的 CI 钉在 `v0.3.0`，而 rules-layer 最新 tag 是 `v0.3.1`
- **THEN** 巡检报告 CI 版本落后，并列出两个版本之间改了哪些共享文件

### Requirement: 不提交、不碰用户未提交的改动

skill MUST NOT 执行 git 提交或推送。工作区有用户未提交改动时，skill 只新增或修改本阶段负责的文件，汇报末尾列出它改了哪些文件，由用户或 gates 决定如何提交。

#### Scenario: boyangcong 有 28 个未提交改动
- **WHEN** 在 boyangcong 跑阶段一
- **THEN** 只新增 `CLAUDE.md`、ruff 配置并修改 `openspec/config.yaml`，其余文件保持原样，汇报列出这三个文件

### Requirement: 每次运行以汇报结束

每次运行 SHALL 以一份汇报结束：识别表、本次做了哪个阶段或巡检、每项验证命令与结果、改动的文件清单、下一步建议（如「再归档 1 个 change 后可装判断层」）。

#### Scenario: 阶段一完成
- **WHEN** 阶段一写完
- **THEN** 汇报包含 `grep -c "^## Code style" CLAUDE.md`、`openspec instructions proposal` 是否含「不做」、ruff 是否能解析继承配置三项验证结果，并提醒用户在交互会话里同意一次外部引入
