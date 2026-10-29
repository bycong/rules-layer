# artifact-rules Specification

## Purpose
规定 OpenSpec 产物（proposal / design / specs / tasks）写法规则的共享基础版只在本仓库一份。OpenSpec 配置不能引用外部文件，接入项目照写进自己的 `openspec/config.yaml`，与基础版的差异由巡检发现。

## Requirements

### Requirement: 产物写法基础版只住本仓库

本仓库 SHALL 维护一份产物写法基础版，至少包含：
- proposal：写明本次不做什么（Non-goals 小节或以「不做」开头的条目）；控制在一到两页，只写为什么和改什么。
- design：每条决策写明被否决的备选与理由；Risks 每行「[风险] → 对策」；Migration Plan 写上线顺序与回滚；列出改动文件与估计行数，apply 后对照，超出一倍说明原因。
- specs：每个 Requirement 至少一个 Scenario，用 WHEN / THEN；用 SHALL / MUST，不用 should / may。
- tasks：每条两小时内可完成，并写明如何验证完成。

#### Scenario: 修改基础版
- **WHEN** 基础版的某条写法需要调整
- **THEN** 只改本仓库那一份，再由巡检报告哪些接入项目与之不一致

### Requirement: 项目照写基础版并只追加不改写

接入项目的 `openspec/config.yaml` 的 `rules` SHALL 包含基础版的全部条目，措辞与基础版一致；项目 MUST NOT 改写或删除基础条目，只能在其后追加本项目的条目，并写明追加原因。`context` 段（项目描述、技术栈、红线）完全属于项目，不受本要求约束。

#### Scenario: 项目追加条目
- **WHEN** Divination 需要说明「2026-10 之前的 design 用另一种 Risks 写法」
- **THEN** 作为追加条目写在基础条目之后，基础条目的措辞不变

#### Scenario: 检查是否一致
- **WHEN** 巡检比较项目 `rules` 与基础版
- **THEN** 基础条目缺失或措辞不同时报告差异，追加条目不报告

### Requirement: 产物写法与判断检查保持一致

基础版中能用正则判死的条目（Risks 行格式、Migration Plan 含回滚）SHALL 由判断层的产物格式 lint 检查；需要理解语义的条目（写明不做什么、决策附备选）SHALL 由判断层基础规则检查，其 `enforces` 指向 `L1/proposal` 或 `L1/design`。基础版修改某条写法时，MUST 同时检查对应的 lint 或基础规则是否仍然一致。

#### Scenario: 放宽 Risks 写法
- **WHEN** 基础版决定同时接受「- **风险** → 对策」写法
- **THEN** 产物格式 lint 同步接受这种写法，两者在同一次改动中完成
