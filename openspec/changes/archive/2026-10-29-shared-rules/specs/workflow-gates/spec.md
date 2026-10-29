## Purpose

规定包住每个 OpenSpec change 的三个自动检查点（方案写完、写代码前、写完代码后）在本仓库只有一份，接入项目引用后只补自己的命令、红线规则清单与额外步骤，并提供可选的「阶段学习文档同步 Notion」步骤。

## ADDED Requirements

### Requirement: 检查点正文只住本仓库

三个检查点的触发时机、步骤顺序、block 与 review 的处理方式 SHALL 在本仓库只有一份正文，接入项目 `CLAUDE.md` 用 `@` 引入，MUST NOT 复制或改写。检查点写在 `CLAUDE.md` 体系里，而不写进 `.claude/commands/opsx/*.md`，因为后者会被 `openspec update` 重新生成。

#### Scenario: 修改一个检查点
- **WHEN** 检查点的处理方式需要调整
- **THEN** 只改本仓库正文，所有接入项目下次会话按新方式执行

#### Scenario: openspec update 之后
- **WHEN** 在接入项目运行 `openspec update`
- **THEN** 检查点仍然生效，因为它不在被重新生成的文件里

### Requirement: 项目只补命令、红线清单与额外步骤

接入项目 SHALL 在引入检查点之后，写明本项目的具体命令（判断、ruff、测试、前端 lint、文案检查各自怎么运行、在哪个目录运行）、实质类红线规则清单，以及本项目额外的步骤。额外步骤 SHALL 插在「写完代码后」检查点的汇报之前，同样逐项汇报。

#### Scenario: 不同的命令前缀
- **WHEN** 章字书用 `cd api && uv run`，Divination 用 `cd backend && . .venv/bin/activate && PYTHONPATH=.`
- **THEN** 两边检查点正文相同，命令差异只写在各自 `CLAUDE.md`

#### Scenario: 项目额外步骤
- **WHEN** Divination 改了 `frontend/index.html`
- **THEN** 在汇报前运行它自己的前端交互回归，结果与其他检查一起逐项汇报

### Requirement: 方案写完立即检查

proposal 或 design 刚写完时（经 `/opsx:continue`、`/opsx:ff`、`/opsx:propose` 或 explore 模式手写），SHALL 立即运行判断检查：格式类 block（产物格式 lint、写明不做什么、决策附备选）是起草失误，由 AI 自行修改后重跑；实质类 block 或 review（项目红线、过度设计）等于改方案，MUST 报告给用户决定。最终结果与改了什么附在给用户的方案汇报里。

#### Scenario: 格式类 block
- **WHEN** 新写的 design 缺少被否决的备选方案
- **THEN** AI 补上备选后重跑，汇报中写明补了什么

#### Scenario: 实质类 block
- **WHEN** 新写的 design 触犯项目红线
- **THEN** AI 不自行改方案，把规则与原文报告给用户，等用户决定

### Requirement: 写代码前再检查一次

apply 写任何代码之前 SHALL 再运行一次判断检查。任一 block MUST 停下，不碰代码，逐条报告规则与原文，等用户决定；只有 review 时用一小段列出后继续。此时不静默修改方案，因为用户已经看过方案。

#### Scenario: 用户改过方案后出现 block
- **WHEN** 用户手改 design 后开始 apply，检查出一条 block
- **THEN** AI 不写代码，报告该条 block 并等待

#### Scenario: 只有 review
- **WHEN** 检查结果只有 review
- **THEN** AI 列出 review 后继续写代码

### Requirement: 写完代码后按顺序检查并逐项汇报

apply 最后一个任务做完、汇报完成之前，SHALL 按顺序执行：
1. 对本次改过的文件运行 `/simplify`。
2. 运行 ruff，修掉报出的问题。
3. 运行不联网测试；改了判断规则或 `JEV_MODEL` 时加跑 Jev 回归。
4. 改了前端时运行前端 lint 并修掉问题。
5. 改了界面文案时运行文案检查；block 必须修，review 列出。
6. 运行项目额外步骤。
完成汇报 MUST 逐项写结果，跳过的写明原因。

#### Scenario: 只改了后端
- **WHEN** 一次 apply 只改了 Python 文件
- **THEN** 汇报包含 `/simplify`、ruff、测试的结果，并写明前端 lint 与文案检查已跳过、原因是未改动前端与文案

#### Scenario: 改了判断规则
- **WHEN** 一次 apply 修改了 `judgments.yaml`
- **THEN** 测试一步加跑 Jev 回归，汇报中写明回归结果

#### Scenario: ruff 报错
- **WHEN** ruff 报出问题
- **THEN** 修掉后重跑直到通过，再进入下一步，汇报中写明修了什么

### Requirement: 项目尚无判断层时只启用不依赖 Jev 的步骤

未装判断层的接入项目 SHALL 只执行「写完代码后」检查点中不依赖 Jev 的步骤（`/simplify`、ruff、不联网测试、前端 lint），方案写完与写代码前两个检查点不执行判断，汇报中写明「判断层未装」。

#### Scenario: 新项目第一个 change
- **WHEN** 刚接入的项目完成第一个 apply
- **THEN** 汇报包含 `/simplify`、ruff、测试、前端 lint 的结果，并写明判断检查因判断层未装而跳过

### Requirement: 可选步骤：阶段学习文档同步 Notion

接入项目 SHALL 能选择启用「阶段学习文档」步骤：项目 `CLAUDE.md` 写明 Notion 落点页面后启用，未写明则不启用。启用后，每完成一个阶段（一个产物写完或一段 apply 完成），AI MUST 主动在落点下新建编号子页，写给零基础读者：做了什么、为什么、要敲的命令、应该看到什么，并注明仓库是权威记录，不等用户提醒。

#### Scenario: 已启用的项目
- **WHEN** 项目写明了 Notion 落点，且一个 change 的 design 刚写完
- **THEN** AI 在落点下新建下一篇编号子页记录这一阶段

#### Scenario: 未启用的项目
- **WHEN** 项目 `CLAUDE.md` 没有写 Notion 落点
- **THEN** 不同步 Notion，汇报中也不提这一步
