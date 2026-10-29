# Tasks

## 1. 识别与巡检脚本

- [ ] 1.1 写 `skills/rules-layer/check.py`：识别表（语言与包管理、后端与前端目录、openspec、归档数、CI 与钉的 rules-layer 版本、未提交改动、各层状态）与 design 决策 5 的七项巡检，最后一行输出下一阶段（一 / 二 / 三 / 巡检 / 先 openspec init）。只读，`uv run --script` 运行。验证：在三个项目各跑一次能输出完整报告；运行前后 `git status` 不变。
- [ ] 1.2 写 `skills/rules-layer/tests/test_check.py`：在临时项目里覆盖无 openspec、未接入、已接入但缺判断层、全部装好、各项巡检命中与不命中、CI 版本落后。验证：`uv run --with pytest --with pyyaml pytest skills/rules-layer/tests` 全部通过；ruff 通过。

## 2. skill 与模板

- [ ] 2.1 写 `skills/rules-layer/SKILL.md`：先跑 `check.py`；按下一阶段执行；动手前列文件等确认；红线与规则候选注明出处、逐条确认；不提交；以汇报结束。验证：对照规格十条需求逐条找到对应步骤，记入 `verification.md`。
- [ ] 2.2 写 `templates/`：`CLAUDE.md` 骨架、`ruff.toml`、`judge.yaml`、`judgments.yaml` 骨架、`judge_cases.yaml` 骨架。验证：模板里 `grep` 不到任何项目名、领域词或本机路径。
- [ ] 2.3 写本仓库 `README.md`（目录、安装 skill 与 `jev-judge`、配置 key、启用提交前钩子）；建软链接 `~/.claude/skills/rules-layer`。验证：新开会话的可用 skill 列表里出现 `rules-layer`。

## 3. 只读试跑

- [ ] 3.1 在章字书、Divination 跑巡检。验证：两项目工作区运行前后不变；每项结论与人工核对一致（Divination CI `v0.3.0` 落后于 `v0.3.1` 应被报出），记入 `verification.md`，不一致处修脚本后重跑。

## 4. boyangcong 阶段一

- [ ] 4.1 在 boyangcong 运行 `/rules-layer`：识别表、阶段一计划、红线候选（注明出处）交用户确认后写 `CLAUDE.md`、`ruff.toml`、`openspec/config.yaml` 的 `rules`。验证：`grep -c "^## Code style" CLAUDE.md` 为 1；`openspec instructions proposal --change <任一>` 含「不做」；`ruff check` 能解析继承配置，报出的问题列进汇报；用户原有 28 个未提交改动不变；不产生提交。
- [ ] 4.2 再跑一次 `check.py`，确认 boyangcong 下一阶段变为阶段二（已归档 5 个，判断层待用户确认规则）。验证：最后一行输出「阶段二」。

## 5. 收尾

- [ ] 5.1 Notion「新项目规则层搭建手册」开头加说明，指向 `/rules-layer` 与本仓库 README。验证：页面开头可见该说明。
- [ ] 5.2 对照 design 估计行数；按本仓库 gates 跑 `/simplify`、ruff、测试。验证：`verification.md` 有对照表与各项结果。

## Workflow follow-up

- 打 tag，归档本 change。
- 在 Notion rules-layer 项目页写下一篇编号学习文档。
