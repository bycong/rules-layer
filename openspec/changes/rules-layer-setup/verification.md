# Verification

## 1. 识别与巡检脚本

### 1.1 `skills/rules-layer/check.py`

在章字书、Divination、boyangcong 各跑一次，运行前后 `git status --porcelain` 的摘要相同（只读）。

首轮试跑发现一处判定错误并已修正：Divination 的 `config.yaml` 在 Risks 那条基础条目同一行末尾加了兼容说明，属于改写基础条目（真实偏离），但脚本把它算成「阶段一产物写法缺」，导致 Divination 下一阶段被判为「阶段一」。改为：只有整段 `rules` 不存在才算阶段一未装；有 `rules` 但与基础版不一致记为巡检发现；整段不存在时不再逐条重复列出。

### 1.2 测试

`skills/rules-layer/tests/test_check.py` 15 条全部通过：不在 git 仓库、历史多但未接入仍从阶段一开始、归档不足与足够时的阶段二、全部装好进巡检、CLAUDE.md 缺引入、ruff 写 select、ESLint 未引入基础规则、改写与追加基础条目的区分、引擎副本、同 id 同内容与有意覆盖的区分、通用词、CI 落后与最新、只读。ruff 通过。用 `uv run --with` 的临时环境跑，未往 miniforge base 装任何包。

## 2. skill 与模板

### 2.1 `SKILL.md` 与规格十条需求对照

| 规格需求 | SKILL.md 落点 |
|---|---|
| skill 只住本仓库 | 开头说明 + README 安装一节（软链接） |
| 先识别再做事 | 第 1 步（跑 check.py，按「下一阶段」分支；无 git / openspec 即停） |
| 按安装状态决定下一步 | 第 1 步分支 + 第 2 步（列计划、等确认）+「一次只做一个阶段」 |
| 阶段一 | 第 3 步 1–6 |
| 红线由人确认 | 「不可违反」第 3 条 + 第 3 步 1 + 第 5 步前提 |
| 阶段二 | 第 4 步 |
| 阶段三 | 第 5 步 1–6 |
| 已装好的只巡检 | 第 6 步 +「不可违反」第 5 条 |
| 不提交、不碰未提交改动 | 「不可违反」第 4 条 + 第 2 步「不会碰的东西」 |
| 以汇报结束 | 第 7 步 |

### 2.2 模板

`templates/` 五份：`CLAUDE.md.tmpl`、`ruff.toml.tmpl`、`judge.yaml`、`judgments.yaml`、`judge_cases.yaml`。`grep` 不到任何项目名、领域词或本机路径。`CLAUDE.md` 与 `ruff.toml` 两份加 `.tmpl` 后缀：原名会被 Claude Code（读取该目录文件时加载同目录 `CLAUDE.md`）与 ruff（向上查找配置）当成真配置。

### 2.3 README 与软链接

新建本仓库 `README.md`（目录、安装 skill / `jev-judge` / key / 钩子、接入与巡检、CI 写法）。`~/.claude/skills/rules-layer` 软链接到本仓库 `skills/rules-layer`；新开非交互会话确认可用 skill 列表里有 `rules-layer`。本仓库 `CLAUDE.md` 命令表补上 skill 脚本的 ruff 与测试命令。

## 3. 只读试跑

章字书与 Divination 运行 `check.py` 前后工作区不变。逐项人工核对：

| 项目 | 脚本结论 | 人工核对 |
|---|---|---|
| 章字书 | 各层已装好；巡检全部一致；下一阶段巡检 | 三条通用规则已从 `judgments.yaml` 删去、15 个通用词已移出词表、无 CI，一致 |
| Divination | 各层已装好；产物写法 `rules.design` 的 Risks 条目被改写；CI 钉 `v0.3.0` 落后 `v0.3.1`，差异只有 `judge/src/jev_judge/judge.py`；下一阶段巡检 | `config.yaml` 在 Risks 基础条目同一行末尾追加了兼容说明（应另起一条追加）；`ci.yml` 两个 job 都钉 `v0.3.0`；`v0.3.0..v0.3.1` 的共享文件差异确为 `judge.py`（/simplify 精简，行为不变），一致 |

两处 Divination 的偏离由用户决定是否处理：Risks 条目改为「基础条目原样 + 另起一条追加说明」；CI 升到 `v0.3.1`。

## 4. boyangcong 阶段一

通过 `/rules-layer` skill 运行（按 `SKILL.md` 步骤）：识别 → 下一阶段「阶段一」→ 列计划 → 红线候选（四条，均出自 `openspec/config.yaml` 的 context）交用户确认，用户四条全选 → 写入。

改动（均未提交）：新增 `CLAUDE.md`（简介、四条红线、两节引入、命令表）、`ruff.toml`（`extend` 基础配置；`build_notes.py`、`review_cli.py` 两个命令行入口豁免 T201 并注明原因）；修改 `openspec/config.yaml`（保留 context，追加 `rules` 段）。

| 验证 | 结果 |
|---|---|
| `grep -c "^## Code style" CLAUDE.md` | 1 |
| `openspec instructions proposal --change geo-audit-service` 含「不做」 | 是 |
| ruff 能解析继承配置 | 能；报出的 I、B 类问题只有基础配置里才有，证明继承生效 |
| 用户原有 29 个未提交改动 | 指纹前后相同 |
| 提交 | 无（HEAD 仍为 `41586b9`） |

ruff 报出、只列不改的问题（9 条）：`bycong/form/app.py` 一处过宽 `except Exception`（BLE001）、两处 `print`（T201，表单服务不是命令行入口）；`bycong/form/tests/test_app.py` 一处注释掉的代码（ERA001）；`build_notes.py` 的 `parse_note` 复杂度 18、一处未用的循环变量（B007）、import 排序；`test_notes.py` 的 `handle_starttag` 复杂度 12、import 排序。

### 4.2 再次识别

首次复跑时脚本仍报「有 Python 代码但没有 ruff 配置」：`check.py` 只看已跟踪文件，而 skill 规定不提交，新建的 `ruff.toml` 看不到。改为已跟踪 + 未被 `.gitignore` 忽略的新文件（三个项目均确认不会扫进 `.venv`、`node_modules`），加测试一条，测试 16 条通过。复跑：三层均已装好，下一阶段「阶段二（已归档 5 个，用户确认候选规则后可进入阶段三）」。章字书、Divination 复跑结论不变（巡检）。

## 5. 收尾

### 5.1 Notion

「新项目规则层搭建手册」开头加了说明：步骤已做成 `/rules-layer`，共享部分在公开仓库 bycong/rules-layer，手册保留作原理说明，「复制 judge.py、复制规矩正文」等步骤已被取代。

### 5.2 行数与写完代码后的检查

| 文件 | 估计 | 实际 | 说明 |
|---|---|---|---|
| `skills/rules-layer/SKILL.md` | +120 | +73 | |
| `skills/rules-layer/check.py` | +220 | +294 | 未超一倍；含识别表、四层、五项巡检与 `collect()` |
| `skills/rules-layer/tests/test_check.py` | +150 | +210 | |
| `skills/rules-layer/templates/`（5 个） | +80 | +67 | |
| `README.md` | +40 | +60 | |
| `skills/rules-layer/ruff.toml` | 未估计 | +6 | 脚本目录需要自己的 ruff 配置（本仓库根目录没有） |
| boyangcong `CLAUDE.md` | +50 | +37 | 未提交 |
| boyangcong `ruff.toml` | +6 | +6 | 未提交 |
| boyangcong `openspec/config.yaml` | +15 | +16 | 未提交 |

1. `/simplify`：对 `check.py` 与测试跑四路审查。采纳：识别、各层、巡检、下一阶段抽成 `collect()`，`main` 与测试共用（测试原来抄了一份流程）；`archived()`、`ci_refs()` 各只算一次；`has_python()` 合并两处判断；锁文件表提成常量 `LOCKFILES`；CI 一行与 ESLint 一行拆开；引擎副本改用 `git grep` 找，不再逐个读 .py 文件；测试改用脚本自己的 `_yaml`、`git`。跳过：`config.yaml` 读两次（几个小文件，不值得改签名）；阶段名兼作逻辑键（单文件、测试已钉住）；CI 正则要求 `ref:` 紧跟 `repository:`、`def load_rules` 作为副本特征、写死 `bycong/rules-layer`（三个项目都符合，第 9 条不为没有调用方的情况加配置）。
2. ruff：`skills/rules-layer` 通过。
3. 测试：16 条通过。精简前后在章字书、Divination、boyangcong 的输出逐字相同（第一次对比时把旧脚本放在临时目录，它按自身位置找不到基础文件，造成假差异；放回原目录后一致）。
4. 前端 lint、文案检查：无，跳过。
