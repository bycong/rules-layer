# shared-code-style Specification

## Purpose
规定代码写法规矩（九条与 Python 落法）和 ruff / ESLint 基础规则在本仓库只有一份，以及接入项目如何引用它们、在哪里补充项目自己的部分，使规矩改一处、所有项目同时生效。

## Requirements

### Requirement: 九条与 Python 落法只住本仓库

不分语言的九条写法原则与 Python 落法 SHALL 各在本仓库有且只有一份正文。接入项目 MUST NOT 复制或改写这两份正文，只能引用；项目要调整某条措辞时 SHALL 改本仓库的正文，使所有接入项目同时生效。

#### Scenario: 查找写法规矩
- **WHEN** 开发者或 AI 想知道某个接入项目的代码该怎么写
- **THEN** 读到的九条与 Python 落法来自本仓库那一份，项目里不存在第二份正文

#### Scenario: 修改一条规矩
- **WHEN** 某条规矩的措辞需要调整
- **THEN** 只改本仓库的正文，章字书与 Divination 下次会话读到的都是新措辞，两个项目都不需要改文件

### Requirement: 项目在 Code style 标题下引用共享规矩

接入项目根目录 `CLAUDE.md` SHALL 保留 `## Code style` 二级标题，标题下用 `@` 引入本仓库的九条与 Python 落法，之后只写本项目的样板文件路径、语言落法所在位置与豁免说明。保留该标题是因为判断规则的 `enforces: L0/Code style` 按标题查找上层规矩。

#### Scenario: 引入后 AI 读到完整规矩
- **WHEN** Claude Code 在接入项目中开始会话
- **THEN** 上下文中包含本仓库九条与 Python 落法的全文，以及项目补充的样板路径

#### Scenario: 判断规则仍能找到上层规矩
- **WHEN** 项目判断规则写 `enforces: L0/Code style`
- **THEN** 项目 `CLAUDE.md` 中能找到 `## Code style` 标题，判断层不报「enforces 指向不存在的上层规则」

#### Scenario: 本仓库与项目不在同一父目录
- **WHEN** 项目被单独 clone 到别处，`@../rules-layer/...` 指向的文件不存在
- **THEN** 引入失败是可见的（会话中缺少九条正文），由 `rules-layer-setup` 的巡检报告缺失，不静默使用旧副本

### Requirement: 前端落法在出现第二个同类项目前留在项目

某种前端形态的落法（如 React、单文件原生 JS）在只有一个项目使用时 SHALL 留在该项目的语言目录 `CLAUDE.md`，不进本仓库；同一形态出现第二个接入项目时，SHALL 先把落法收进本仓库再接入第二个项目，不复制。

#### Scenario: 当前状态
- **WHEN** 查看本仓库的语言落法
- **THEN** 只有 Python 落法；章字书 `web/CLAUDE.md` 的 React 落法与 Divination `frontend/CLAUDE.md` 的单文件落法各留原处

#### Scenario: 第二个 React 项目接入
- **WHEN** 一个新的 React 项目要接入规则层
- **THEN** 先把章字书的 React 落法收进本仓库、章字书改为引用，再让新项目引用，过程中不存在两份 React 落法

### Requirement: ruff 基础规则由项目继承

本仓库 SHALL 提供一份 ruff 基础配置：选用规则 ERA001（注释掉的代码）、T201（print）、BLE001（过宽 except）、C901（圈复杂度），复杂度上限 10。接入项目的 ruff 配置 SHALL 继承它，只写本项目的豁免路径；每条豁免 MUST 写明原因，MUST NOT 在代码中逐行加 noqa。

#### Scenario: 项目继承基础规则
- **WHEN** 在章字书 `api/` 或 Divination `backend/` 运行 ruff
- **THEN** 生效的选用规则与复杂度上限来自本仓库，项目配置里只出现豁免

#### Scenario: 基础规则调整
- **WHEN** 本仓库的基础配置新增一条选用规则
- **THEN** 两个项目下次运行 ruff 即按新规则检查，项目配置不需要改

#### Scenario: 继承前后结果一致
- **WHEN** 两个项目从自带规则改为继承基础配置
- **THEN** 迁移前后 ruff 对同一份代码的报告完全相同

### Requirement: ESLint 基础规则由项目继承

本仓库 SHALL 提供一份 ESLint 基础规则：`no-console` 与 `no-nested-ternary` 为报错级别，函数复杂度目标上限 15。接入项目的 ESLint 配置 SHALL 引入这份基础规则，再加本项目的框架规则与豁免。项目当前代码超出复杂度目标时，SHALL 把上限设为当前最复杂函数的值并写明原因与递减计划，上限只降不升。

#### Scenario: 章字书引入基础规则
- **WHEN** 在章字书 `web/` 运行 lint
- **THEN** `no-console`、`no-nested-ternary`、复杂度 15 来自本仓库，中文字面量等 React 专属规则仍在项目配置

#### Scenario: Divination 使用复杂度棘轮
- **WHEN** Divination 前端当前最复杂函数为 35
- **THEN** 项目配置把复杂度上限设为 35 并写明「目标 15，只降不升」，其余基础规则照常生效

#### Scenario: 继承前后结果一致
- **WHEN** 两个项目从自带规则改为引入基础规则
- **THEN** 迁移前后 lint 的报告完全相同
