# judge-engine Specification

## Purpose
规定 Jev 判断引擎 `jev-judge` 只在本仓库一份：项目在自己根目录用同一个命令审方案与文案，需要时从代码里 import 同一个库；项目差异写在项目配置里，通用判断规则与通用短标签词表随引擎提供。

## Requirements

### Requirement: 引擎只住本仓库

判断引擎 SHALL 在本仓库只有一份代码，以一个 Python 包提供命令行与库两种用法。接入项目 MUST NOT 保留引擎副本；项目修引擎问题时 SHALL 改本仓库，所有接入项目同时生效。

#### Scenario: 修一个引擎问题
- **WHEN** 引擎的某个判定逻辑需要修改
- **THEN** 只改本仓库，章字书与 Divination 下次运行即用上新逻辑，两个项目都不改文件

#### Scenario: 项目里不再有副本
- **WHEN** 迁移完成后在两个项目里查找 `judge.py`
- **THEN** 只剩与判断层无关的文件（如 Divination 的 `app/eval/judge.py`），没有判断引擎副本

### Requirement: 命令在项目根目录运行

命令 `jev-judge` SHALL 在任一接入项目内运行，以当前目录所在 git 仓库的根为项目根，读取该项目的 `openspec/`。参数与原先一致：`--change <name>` 审 `openspec/changes/<name>` 或 `archive/<name>` 下的产物，`--copy` 审相对主分支新增或修改的界面文案，`--lint-only` 只跑正则检查不联网，`--dry-run` 打印将要发送的请求而不发送。

#### Scenario: 在子目录运行
- **WHEN** 在章字书的 `api/` 目录下运行 `jev-judge --change adopt-shared-rules`
- **THEN** 引擎以章字书仓库根为项目根，审 `openspec/changes/adopt-shared-rules` 下的产物

#### Scenario: 不在 git 仓库里
- **WHEN** 在一个不属于任何 git 仓库的目录运行
- **THEN** 以非 0 退出码报错，说明需在接入项目内运行

### Requirement: 库接口名称保持不变

引擎 SHALL 以库的形式提供 `load_rules`、`Rule`、`Judge`、`verdict_or_pending`、`lint_design`、`lint_copy`、`label_len`、`enforces_exists`、`change_files`、`lexicon`、`pick_provider`，名称与含义和两个项目原先的 `judge.py` 一致，项目代码只需改 import 一行。

#### Scenario: 章字书对话评估集
- **WHEN** `tests/eval/test_chat_eval.py` 改为从 `jev_judge` import
- **THEN** 不改其他代码即可运行，结果与迁移前一致

### Requirement: 项目差异写在项目配置

文案文件的位置、格式（嵌套 JSON，或 HTML 内的 JS 对象）、取哪种语言，以及项目自己的文案禁词，SHALL 写在项目的 `openspec/judge.yaml`，引擎不写死任何项目的路径或词语。项目没有配置文案时，`--copy` MUST 以非 0 退出码报错并说明缺少哪项配置。

#### Scenario: 章字书审文案
- **WHEN** 章字书配置文案为 `web/messages/zh.json`、格式为嵌套 JSON
- **THEN** `jev-judge --copy` 审该文件相对主分支新增或修改的条目

#### Scenario: Divination 审文案
- **WHEN** Divination 配置文案为 `frontend/index.html`、格式为 HTML 内 JS 对象、语言 `zh-Hans`，禁词含「保证应验」等
- **THEN** `jev-judge --copy` 只审简体那一套，含禁词的条目在 lint 阶段 block

### Requirement: 通用判断规则随引擎提供

「写明不做什么」「决策附备选」「不做过度设计」三条通用判断规则 SHALL 随引擎提供，所有接入项目自动启用；项目 `openspec/judgments.yaml` 只写本项目的规则。项目规则与通用规则同 id 时 SHALL 以项目规则为准。通用规则的 `enforces` 按项目自己的 `CLAUDE.md` 与 `openspec/config.yaml` 检查。

#### Scenario: 迁移后项目规则文件变短
- **WHEN** 章字书与 Divination 从各自 `judgments.yaml` 删去三条通用规则
- **THEN** 运行判断时这三条照常出现，问题、阈值与迁移前一字不差

#### Scenario: 项目收紧一条通用规则
- **WHEN** 项目在自己的 `judgments.yaml` 写了同 id 的 `design-decisions-have-alternatives` 并调高 block 阈值
- **THEN** 该项目使用自己的版本，其他项目仍用通用版本

### Requirement: 通用短标签词表随引擎提供

引擎 SHALL 带一份通用短标签词表，只收不属于任何领域的控件与状态标签（如「重试」「收起」「关闭」「加载中…」）。审短标签时通用词表与项目词表任一包含即 pass。领域词 MUST NOT 进通用词表。

#### Scenario: 通用标签不必进项目词表
- **WHEN** 新项目界面新增「重试」，项目词表为空
- **THEN** 查通用词表命中，pass

### Requirement: key 只放一处

Jev 的 key SHALL 从环境变量 `TYPESAFE_API_KEY` 读取；未设置时读 `~/.config/jev-judge/env`。引擎 MUST NOT 读取项目目录里的 `.env`。裁判选择规则不变：未指定时有 key 用 Jev、无 key 用人工模式；指定 Jev 却没有 key 时以非 0 退出码报错，不悄悄退化。

#### Scenario: 新项目接入不用再放 key
- **WHEN** 一个新项目接入，项目里没有任何 key
- **THEN** 引擎读到 `~/.config/jev-judge/env` 中的 key，使用 Jev

#### Scenario: 没有 key 时预览请求
- **WHEN** 没有 key，运行 `jev-judge --change x --dry-run`
- **THEN** 打印将要发给 Jev 的请求内容，不报错、不发送

### Requirement: 判定口径与迁移前一致

引擎合并 SHALL 不改变判定口径：pass / review / block 的阈值算法、置信度规则、`JEV_MODEL` 固定版本、有 block 时退出码非 0，均与两个项目原先一致。两个项目迁移前后，同一批回归用例的结果 MUST 相同。

#### Scenario: 迁移前后回归对比
- **WHEN** 两个项目改用 `jev-judge` 后重跑 Jev 回归
- **THEN** 通过与失败的用例集合与迁移前完全相同
