---
name: rules-layer
description: 在项目根目录给项目接入或巡检 AiDevelopProjects 共享规则层（rules-layer）：识别项目、补上下一个未装的阶段（代码规矩与 gates、候选判断规则、判断层），已装好的项目只巡检并报告与共享版本的偏离。用户说「接入规则层」「/rules-layer」「巡检规则层」「这个项目装规则」时使用。
---

# /rules-layer：接入与巡检规则层

共享规则只住 `~/AiDevelopProjects/rules-layer`（下称本仓库）。本 skill 不把任何共享正文复制进项目，只写项目自己的部分并引用共享部分。

## 不可违反

- **先识别后动手**：第 1 步的脚本结论决定做什么，不凭印象判断阶段。
- **一次只做一个阶段**：做之前列出要新增、修改的文件，用户同意后才写。
- **红线与判断规则由用户确认**：候选要注明出处（README、`openspec/config.yaml` 的 context、某个已归档方案）；没确认的不写。
- **不提交、不推送**：工作区里用户已有的改动一律不碰；汇报末尾列出本次改了哪些文件。
- **巡检只报告**：已装好的项目不改任何文件。

## 1. 识别

在项目根目录运行：

```bash
uv run -q --script ~/AiDevelopProjects/rules-layer/skills/rules-layer/check.py
```

把输出的识别表、各层状态、巡检原样放进汇报。最后一行「下一阶段」决定第 2 步走哪个分支。

- 「先在 git 仓库里运行」或「先 openspec init」：告诉用户，停止。
- 「阶段一」→ 第 3 步。
- 「阶段二」→ 第 4 步；说明里写「可进入阶段三」且用户确认了规则 → 第 5 步。
- 「巡检」→ 第 6 步。

## 2. 列计划，等确认

按将要执行的阶段，列出：要新增的文件、要修改的文件（写明改哪一段）、不会碰的东西（「其余 N 个未提交改动不变」）。用户同意前不写任何文件。

## 3. 阶段一：代码规矩、gates、产物写法、lint

1. **红线候选**：从项目 README、`openspec/config.yaml` 的 `context` 里找出「绝对不能做的事」，每条注明出处，逐条请用户确认、改写或删除。没有找到也要问用户一句。
2. **`CLAUDE.md`**：按 `templates/CLAUDE.md.tmpl` 写，填项目简介、确认过的红线、样板路径、本项目命令表。命令表里判断与文案检查写「判断层未装」；ruff、测试、前端 lint 按项目实际命令写，没有的写「无，跳过」。已有 `CLAUDE.md` 时只补缺的两节，不改其他内容。
3. **`openspec/config.yaml`**：保留原有 `context`，把本仓库 `openspec-base/artifact-rules.yaml` 的 `rules` 段原样写入（已有 `rules` 段时只补缺的基础条目，项目自己的条目放在基础条目之后）。
4. **lint**：有 Python 代码时，项目已有 `pyproject.toml` 就在 `[tool.ruff]` 写 `extend`，否则在根目录按 `templates/ruff.toml.tmpl` 建 `ruff.toml`（`extend` 的相对路径从该文件所在目录算到本仓库的 `lint/ruff-base.toml`）。有 ESLint 配置时 import 本仓库 `lint/eslint-base.mjs` 并展开进规则。不为没有的语言建配置。
5. **验证**（结果写进汇报）：
   - `grep -c "^## Code style" CLAUDE.md` 为 1；
   - `openspec instructions proposal --change <任一 change>` 的输出含「不做」（没有进行中的 change 时，用 `openspec new change rules-layer-probe` 建一个、看完删掉）；
   - 运行 ruff，能解析继承配置；报出的问题列进汇报，**不自动修代码**。
6. 提醒用户：在本项目开一次交互会话，同意读取项目外文件（`@../rules-layer/...`），然后问「九条第 9 条是什么」确认生效。

## 4. 阶段二：候选判断规则

1. 读 `openspec/changes/archive/` 下各 change 的 `proposal.md` 与 `design.md`，找出反复出现、且能指回已写下规矩（`CLAUDE.md` 某个二级标题、`config.yaml` 的 rules 或 context、某份规格）的问题。
2. 每条候选写：规则 id（kebab-case）、要问 Jev 的一句正向陈述、`expect`、`enforces`、出现在哪几个 change。三条通用规则（写明不做什么、决策附备选、不做过度设计）引擎已自带，不列。
3. 已归档不足 3 个时，写明还差几个，不进入阶段三。
4. 候选只写在汇报里，不建文件。

## 5. 阶段三：判断层

前提：已归档至少 3 个，且用户确认了至少一条阶段二的候选规则。

1. `openspec/judgments.yaml`：按 `templates/judgments.yaml`，只写用户确认的规则；红线规则 `thresholds` 的 block 起始为 0（只 review 不拦），文件里注明。
2. `openspec/judge.yaml`：按 `templates/judge.yaml`；项目有界面文案才写 `copy` 段（嵌套 JSON 用 `json`，HTML 内 `const I18N` 用 `js-i18n` 加 `lang`），有项目禁词才写 `banned`。
3. 回归用例骨架：按 `templates/judge_cases.yaml` 放在项目测试目录；每条确认的规则至少列出一个待人工标注的用例位置。
4. `CLAUDE.md` 命令表的判断与文案检查改为 `jev-judge --change <name>`、`jev-judge --copy`。
5. 检查 `which jev-judge` 与 `~/.config/jev-judge/env`：缺命令时给 `uv tool install -e ~/AiDevelopProjects/rules-layer/judge`；缺 key 时给创建该文件的步骤，**不代填 key**。
6. **验证**：`jev-judge --change <一个已归档 change> --lint-only` 不报 enforces 指向不存在；有 key 时再跑一次不带 `--lint-only` 的，结果写进汇报。

## 6. 巡检

只读，不改文件。按 `check.py` 的「巡检」部分逐项说明：一致的写「一致」；有偏离的写出文件、内容和建议怎么改（由用户决定改不改）。CI 版本落后时，列出两版之间改动的共享文件，提醒升级前在项目里跑一遍 lint 与测试。

## 7. 汇报

按顺序：识别表 → 本次做了哪个阶段或巡检 → 每项验证命令与结果 → 本次新增、修改的文件清单 → 没碰的东西（未提交改动数）→ 下一步建议（如「再归档 1 个 change 后可装判断层」「在交互会话同意外部引入」）。
