# Tasks

## 1. rules-layer：引擎包

- [x] 1.1 建 `judge/pyproject.toml`（包名 `jev-judge`，命令 `jev-judge`，`requires-python >= 3.11`，依赖 typesafe-sdk、pyyaml、pydantic、json5）与 `src/jev_judge/__init__.py`。验证：`uv tool install -e judge` 成功，`jev-judge --help` 打印四个参数。
- [x] 1.2 合并引擎到 `src/jev_judge/judge.py`：以 Divination 版为底，补回章字书的 `chat` target 与人工模式 `--dry-run`；项目根取 git 根并要求有 `openspec/`；读 `openspec/judge.yaml`（文案文件、格式 json / js-i18n、语言、禁词）；key 与裁判按环境变量 → `~/.config/jev-judge/env` 读取。对照 Notion 方案 4.4 节差异清单逐项核对。验证：差异清单每项在 `verification.md` 记录落在哪一行；`ruff check` 通过。
- [x] 1.3 建 `base/judgments.yaml`（三条通用规则，取自两个项目、逐字相同）与 `base/copy-lexicon.yaml`（通用短标签：从章字书词表挑不属于任何领域的标签）；引擎先读基础规则再读项目规则，同 id 以项目为准；短标签查两份词表。验证：脚本比对三条规则与两个项目原文逐字相同；通用词表逐条人工过目无领域词，结果记入 `verification.md`。
- [x] 1.4 写 `judge/tests/test_engine.py`：合并两个项目测试中与项目无关的部分，另加配置解析、两种文案格式、同 id 覆盖、不在接入项目时报错、无 key 时 dry-run。验证：`uv run --project judge pytest` 全部通过。
- [x] 1.5 写 `~/.config/jev-judge/env`（key 从章字书 `api/.env` 移过来，不进任何仓库）；在 rules-layer 与章字书根目录各跑一次 `jev-judge --change <已有 change>`。验证：两处都用 Jev 判定成功；`git grep TYPESAFE_API_KEY=` 在本仓库无结果。
- [x] 1.6 本仓库 `CLAUDE.md` 命令表：判断改为 `jev-judge`，ruff 与测试改为针对 `judge/`；`rules/copy-voice.md` 短标签一节改为「通用词表与项目词表一起查」；提交并打 tag `v0.3.0`（`v0.2.0` 留给同期的 `ruff-base-more-rules`）。验证：本仓库新会话按命令表跑判断成功；`git ls-remote --tags origin` 有 `v0.3.0`。

## 2. 章字书迁移

- [x] 2.1 开 change `adopt-jev-judge`：code-style（Python 样板改为引擎文件）与 judgment-rules（引擎位置、配置文件、key 位置）的 MODIFIED 增量；按章字书 gates 跑判断。验证：`openspec validate adopt-jev-judge --strict` 通过；判断无 block。
- [x] 2.2 存迁移前输出：`uv run ruff check app ../pipeline`、不联网测试、Jev 回归（含对话评估集若可离线运行的部分）、`judge --change <已归档 change>`、`judge --copy`。验证：输出文件都在。
- [x] 2.3 加 `openspec/judge.yaml`；删 `api/app/ai/judge.py`；`openspec/judgments.yaml` 删三条通用规则；`copy-lexicon.yaml` 删已进通用词表的词；`pyproject.toml` 换成可编辑路径依赖并删去 `judge.py` 的 ruff 豁免；`app/core/config.py` 删两个字段；`test_chat_eval.py` 改 import；`test_judge.py` 只留回归；`CLAUDE.md` 命令表与样板路径改用引擎。验证：全仓 grep 无 `app.ai.judge`、`typesafe_api_key`、`judge_provider` 残留。
- [x] 2.4 对比迁移前后：ruff 通过；不联网测试通过；Jev 回归失败集合与迁移前相同；`jev-judge --change`、`--copy` 输出与迁移前相同。验证：对比结果记入 `verification.md`，不同之处逐条说明。
- [x] 2.5 删 `api/.env` 中的 key（文件不进仓库，只在本机）；提交章字书。验证：`git log` 有该提交；无 key 的 `api/.env` 下 `jev-judge` 仍用 Jev。

## 3. Divination 迁移（等 CI 能检出 rules-layer 后进行）

- [x] 3.1 开 change `adopt-jev-judge`（code-style 样板、judgment-rules），跑 gates。验证：`openspec validate --strict` 通过；判断无 block。
- [x] 3.2 存迁移前输出（ruff、不联网测试、Jev 回归、`--change`、`--copy`）。验证：输出文件都在。
- [x] 3.3 加 `openspec/judge.yaml`（`frontend/index.html`、js-i18n、`zh-Hans`、八个叙事禁词）；删 `backend/app/rules/judge.py`；`judgments.yaml` 删三条通用规则；`requirements-dev.txt` 改为 `-e ../../rules-layer/judge`；`ruff.toml` 删 `judge.py` 豁免；`test_judge.py` 只留回归；`CLAUDE.md` 命令表与样板路径；CI 在检出 rules-layer 后加 `pip install -e ../rules-layer/judge`。验证：全仓 grep 无 `app.rules.judge` 残留。
- [x] 3.4 对比迁移前后（同 2.4），并推送后 CI 通过。验证：对比结果记入 `verification.md`；CI 绿。
- [x] 3.5 删 `backend/.env` 中的 key；提交。验证：`git log` 有该提交。

## 4. 收尾

- [x] 4.1 对照 design「改动文件与估计行数」，超出一倍的写明原因。验证：`verification.md` 有对照表。
- [x] 4.2 按本仓库 gates 跑写完代码后的检查：`/simplify` 引擎与测试、ruff、引擎测试。验证：完成汇报逐项列出结果。

## Workflow follow-up

- 先归档 `shared-rules`，再归档本 change（`copy-voice` 的修改要求主规格已存在）。
- 归档两个项目的 `adopt-jev-judge`。
- 两个项目 CI 中的 rules-layer 版本改为 `v0.3.0`。
- 在 Notion rules-layer 项目页写下一篇编号学习文档。
