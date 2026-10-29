# Proposal

## Why

Jev 判断层在两个项目各有一份：章字书 `api/app/ai/judge.py` 365 行，Divination `backend/app/rules/judge.py` 403 行，相差 136 行。修一个 bug 要改两遍，第三个项目接入时还要再抄一份。judge 审的是 openspec 里的 markdown 与界面文案，本来不需要住在某个项目的后端里；手册「后端换语言时判断层另行设计」的限制也是放错位置造成的。

本 change 是三步中的第二步，依赖 `shared-rules` 已经把 gates 收回共享。

## What Changes

- **合并成一个引擎**：以 Divination 的 `judge.py` 为底（已改用环境变量、复用连接、Risks 行接受两种写法、`report()` 不在推导式里做副作用），补回章字书的 `chat` target 与人工模式下的 `--dry-run` 行为（没有 key 也能看到要发给 Jev 的请求）。
- **两种用法**：做成 Python 包 `jev-judge`。命令行用 `uv tool install -e` 装成全局命令，在任何项目根目录运行；需要 import 的项目（章字书对话评估集）加成可编辑路径依赖，现有 `load_rules`、`Rule`、`Judge`、`verdict_or_pending` 名字不变。
- **项目差异改成配置**：仓库根目录取当前 git 根；文案文件、格式（嵌套 JSON / HTML 内 JS 对象）与语言由项目配置；项目禁词（如 Divination 的叙事禁词）移入项目自己的判断规则，引擎只保留通用禁用。
- **基础规则继承**：通用 3 条（写明不做什么、决策附备选、不做过度设计）随引擎提供，项目 `judgments.yaml` 继承后只写自己的红线。
- **通用短标签词表**：本仓库提供一份不属于任何领域的短标签词表（重试、收起、关闭、加载中…），引擎同时查通用词表与项目词表；两个项目随后从各自词表移出通用词。
- **key 一处存放**：`TYPESAFE_API_KEY` 从全局位置读取，不再每个项目各放一份。
- **测试拆分**：阈值算法、lint、裁判选择这些通用测试随引擎走；回归用例 `judge_cases.yaml` 留在各自项目。
- **迁移两个项目**：删除各自的 `judge.py` 副本；**BREAKING**（对这两个项目）：判断命令从 `python -m app.ai.judge` / `python -m app.rules.judge` 改为 `jev-judge`，共享 gates 中的判断命令同步改为 `jev-judge`。
- 不做：改动任何判断规则的问题措辞、阈值，或 `JEV_MODEL` 版本；合并只动引擎代码，不动判断口径，两个项目迁移前后回归结果必须一致。
- 不做：产品侧新用法（RAG 打分、guardrails），只保证现有 `chat` 评估继续能用。
- 不做：记录每次运行结果供规则升降级使用，迁移完成后另开 change。
- 不做：TypeScript 版引擎、CI 接入。

## Capabilities

### New Capabilities

- `judge-engine`：`jev-judge` 的命令行与库接口、项目配置、基础规则继承、key 读取、pass / review / block 判定与退出码。

### Modified Capabilities

- `copy-voice`：短标签查词表从「只查项目词表」改为「通用词表与项目词表一起查」。

（章字书 `openspec/specs/judgment-rules` 的契约随迁移改为引用 `judge-engine`，在章字书侧另开 change 处理。）

## Impact

- 新增：本仓库 `judge/` 包（引擎、基础规则、通用测试）；全局命令 `jev-judge`。
- 章字书：删除 `api/app/ai/judge.py`；`api/pyproject.toml` 加可编辑依赖、去掉 `judge` 依赖组；`tests/test_judge.py` 拆分；`tests/eval/test_chat_eval.py` 改 import；`api/.env` 不再放 key。
- Divination：删除 `backend/app/rules/judge.py`；`requirements-dev.txt` 改为可编辑依赖；叙事禁词移入 `openspec/judgments.yaml`；`backend/.env` 不再放 key。
- 依赖：`typesafe-sdk`、`pyyaml`、`pydantic`、`json5`（仅 HTML 内 JS 对象格式需要）。
