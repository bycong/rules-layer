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
