# Design

## Context

动机见 proposal.md「Why」，要求见 `specs/judge-engine` 与 `specs/copy-voice`。影响做法的现状：

- 两份引擎：章字书 `api/app/ai/judge.py`（365 行，uv，Python 3.12，从 `app.core.config.settings` 读 key 与裁判），Divination `backend/app/rules/judge.py`（403 行，pip + venv，Python 3.11，从环境变量读）。逐项差异与合并基准已在 Notion「规则层跨项目共享」方案 4.4 节定下：以 Divination 版为底，补回章字书的 `chat` target 与人工模式下的 `--dry-run`。
- 三条通用判断规则在两个项目里逐字相同，可直接收进引擎。
- 两个项目的测试用到的引擎接口，除 `settings`、`ROOT`、`COPY_FILE` 外名称一致。
- 两个项目的 code-style 规格把各自的 `judge.py` 写成 Python 样板；judgment-rules 规格写着引擎路径、`.env` 位置与 `JUDGE_PROVIDER`。
- Divination 有 CI 并会跑 pytest；它的 rules-layer 接入（`chore/adopt-rules-layer`）要等 CI 能检出本仓库才能上线，由另一个会话处理。
- `copy-voice` 主规格要等 `shared-rules` 归档后才存在，本 change 对它的修改要在那之后归档。

## Goals / Non-Goals

**Goals:**
- 一份引擎，两种用法；项目里只剩配置、项目规则、词表与回归用例。
- 两个项目迁移前后，ruff、离线测试与 Jev 回归结果不变。

**Non-Goals:**
- 不改判断规则的问题、阈值、`JEV_MODEL`。
- 不记录运行结果供规则升降级使用（迁移后另开 change）。
- 不做 TypeScript 版、不发布到 PyPI。

## Decisions

### 1. 包放在 `rules-layer/judge/`，基础规则与通用词表是包内数据

```
judge/
├── pyproject.toml                 包名 jev-judge，命令 jev-judge
├── src/jev_judge/
│   ├── __init__.py                导出库接口
│   ├── judge.py                   引擎（合并后的单文件，结构沿用原 judge.py）
│   └── base/
│       ├── judgments.yaml         三条通用判断规则
│       └── copy-lexicon.yaml      通用短标签词表
└── tests/test_engine.py           与项目无关的引擎测试
```

- 被否决：基础规则放在 `rules/` 下。引擎要跨出包目录找文件，安装方式一变路径就断。
- 被否决：拆成多个模块。原文件 400 行、两个项目都已按九条改写为样板，结构清楚；拆分会让迁移前后难以逐段对照。

### 2. 项目配置写在 `openspec/judge.yaml`

```yaml
copy:
  file: web/messages/zh.json       # 相对项目根
  format: json                     # json | js-i18n
  lang: zh-Hans                    # 只有 js-i18n 需要
banned: []                         # 项目文案禁词，lint 阶段 block
```

没有 `copy` 段时 `--copy` 报错退出。

- 被否决：写进 `pyproject.toml` 的 `[tool.jev-judge]`。非 Python 项目没有这个文件，而判断层审的是 openspec 产物，与后端语言无关。
- 被否决：写在 `judgments.yaml` 开头。那个文件是规则列表，混入配置后结构不一致，校验也要特判。

### 3. 项目根取当前目录所在 git 仓库的根，并要求有 `openspec/`

用 `git rev-parse --show-toplevel` 取根；根下没有 `openspec/` 时报错，提示需在接入项目内运行。

- 被否决：沿用 `Path(__file__).parents[3]`。引擎不再住在项目里，这个写法失去意义。
- 被否决：从当前目录逐级向上找 `openspec/`。仓库里若有嵌套的 `openspec/`（如子项目），会先停在错误的那一层；git 根只有一个，范围明确，且接入项目都是 git 仓库。

### 4. key 先读环境变量，再读 `~/.config/jev-judge/env`

`TYPESAFE_API_KEY` 与 `JUDGE_PROVIDER` 都按这个顺序读；不读项目目录里的 `.env`。章字书 `app/core/config.py` 删去 `typesafe_api_key`、`judge_provider` 两个字段；对话评估集改用引擎的 `pick_provider`。

- 被否决：继续读项目 `.env`。每接入一个项目就要多放一份 key，且两个项目的 `.env` 位置不同（`api/`、`backend/`），引擎得为每个项目特判。
- 被否决：只读环境变量。每开一个终端都要先 export，忘了就悄悄落到人工模式。

### 5. 通用规则自动加载，项目同 id 规则覆盖

引擎先读包内 `base/judgments.yaml`，再读项目 `openspec/judgments.yaml`；同 id 时用项目的。`enforces` 一律按项目的 `CLAUDE.md` 与 `openspec/config.yaml` 检查。

- 被否决：项目写 `extends: base` 才加载。多一项配置，而没有任何项目不想要通用规则。

### 6. 安装：命令用 `uv tool install -e`，import 用可编辑路径依赖

- 命令：`uv tool install -e ~/AiDevelopProjects/rules-layer/judge`。
- 章字书：`api/pyproject.toml` 去掉 `judge` 依赖组，加 `jev-judge = { path = "../../rules-layer/judge", editable = true }`。
- Divination：`requirements-dev.txt` 去掉 `typesafe-sdk`、`json5`，加 `-e ../../rules-layer/judge`；CI 在检出 rules-layer 之后加 `pip install -e ../rules-layer/judge`。

依赖：`typesafe-sdk>=0.7.5`、`pyyaml`、`pydantic>=2`、`json5`，`requires-python >= 3.11`。

- 被否决：发布到 PyPI。一个人用，发版流程比收益重。
- 被否决：`json5` 做成可选依赖（只有 js-i18n 格式要用）。包很小，做成可选要多一层安装说明，Divination 还得记得装可选组。

### 7. 测试拆分：引擎测试进本仓库，回归用例留项目

两个项目 `test_judge.py` 里与项目无关的测试（阈值算法、lint、短标签长度、裁判选择、enforces 检查）合并进 `judge/tests/test_engine.py`，另加配置解析与两种文案格式的测试。项目保留 `tests/judge_cases.yaml` 与一个只跑回归的 `test_judge.py`。

- 被否决：回归用例也收进本仓库。例句与红线属于项目，收进来就违反「项目专属的只放项目」。

### 8. 先迁章字书，Divination 等 CI 接好后再迁

章字书没有 CI，迁移后本地验证即可。Divination 的 rules-layer 接入分支正由另一个会话处理，CI 改动要一次做完（检出 rules-layer + 安装引擎），本 change 在 Divination 的部分排在那之后。

- 被否决：两个项目一起迁。Divination 当前分支状态不由本会话掌握，同时改容易冲突。

### 9. 样板与规格随迁移更新

两个项目的 Python 样板从各自的 `judge.py` 改为 `rules-layer/judge/src/jev_judge/judge.py`；code-style 与 judgment-rules 两份规格在各自项目开小 change 修改（章字书 `adopt-jev-judge`，Divination 同名）。

- 被否决：各项目另选一个本地文件当样板。现在没有比引擎更合适、且已按九条改写过的文件。

## Risks / Trade-offs

- [合并时漏掉两份引擎的某项行为差异] → 以 4.4 节差异清单逐项核对；引擎测试覆盖两种文案格式、人工模式与 dry-run；两个项目迁移前后跑同一批回归逐条对比
- [在不是接入项目的目录运行，误审别的仓库] → 根下没有 `openspec/judgments.yaml` 时报错退出
- [全局命令与项目虚拟环境里的引擎版本不一致] → 两处都以可编辑方式指向同一源码目录
- [Divination CI 跑 pytest 时 import 不到引擎] → CI 加安装步骤，与 shared-rules 的检出步骤一起上线
- [章字书 settings 删字段后，别处还在读] → 删除前全仓 grep `typesafe_api_key`、`judge_provider`，只允许测试与评估集两处，迁移时一并改
- [归档顺序错误导致 copy-voice 增量被拒] → 先归档 `shared-rules`，再归档本 change

## Migration Plan

1. 本仓库：建 `judge/` 包与引擎测试，`uv tool install -e` 装全局命令，key 写入 `~/.config/jev-judge/env`。本仓库 CLAUDE.md 的命令表改用 `jev-judge`，Python 代码开始适用 ruff 与测试。
2. 章字书：开 `adopt-jev-judge` → 存迁移前输出与回归 → 加 `openspec/judge.yaml`、删引擎副本与三条通用规则、通用词移出词表、改依赖与 settings、拆测试 → 对比 → 一个提交。
3. Divination：等 CI 接好 rules-layer 后，同样步骤，CI 加安装引擎一步。

回滚：每个项目是一个提交，`git revert` 即恢复项目里的 `judge.py` 与原依赖；本仓库的引擎不影响未迁移的项目。

## 改动文件与估计行数

| 位置 | 文件 | 估计 |
|---|---|---|
| rules-layer | `judge/pyproject.toml` | +25 |
| | `judge/src/jev_judge/__init__.py` | +15 |
| | `judge/src/jev_judge/judge.py` | +440 |
| | `judge/src/jev_judge/base/judgments.yaml` | +35 |
| | `judge/src/jev_judge/base/copy-lexicon.yaml` | +20 |
| | `judge/tests/test_engine.py` | +180 |
| | `CLAUDE.md` | ±10 |
| | `rules/copy-voice.md` | ±4 |
| 章字书 | `api/app/ai/judge.py` | −365 |
| | `api/app/core/config.py` | −2 |
| | `api/pyproject.toml` | ±6 |
| | `api/tests/test_judge.py` | −110 |
| | `api/tests/eval/test_chat_eval.py` | ±3 |
| | `openspec/judge.yaml` | +4 |
| | `openspec/judgments.yaml` | −25 |
| | `openspec/copy-lexicon.yaml` | −15 |
| | `CLAUDE.md` | ±4 |
| | `adopt-jev-judge` 规格增量 | +60 |
| Divination | `backend/app/rules/judge.py` | −403 |
| | `backend/requirements-dev.txt` | ±3 |
| | `backend/ruff.toml` | −1 |
| | `backend/tests/test_judge.py` | −150 |
| | `openspec/judge.yaml` | +8 |
| | `openspec/judgments.yaml` | −25 |
| | `CLAUDE.md` | ±4 |
| | `.github/workflows/ci.yml` | +2 |
| | `adopt-jev-judge` 规格增量 | +60 |
