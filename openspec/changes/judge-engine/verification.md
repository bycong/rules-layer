# Verification

## 1. 引擎包

### 1.1 安装与命令

`uv tool install -e ./judge` 安装出 `~/.local/bin/jev-judge`；`jev-judge --help` 列出 `--change`、`--copy`、`--lint-only`、`--dry-run` 四个参数。

### 1.2 合并：差异清单逐项落点（`judge/src/jev_judge/judge.py`，共 495 行）

对照 Notion「规则层跨项目共享与 /rules-layer skill 方案」4.4 节。

| 4.4 差异 | 处理 | 位置 |
|---|---|---|
| 仓库根目录写死 `parents[3]` | 改为当前目录所在 git 根，且须有 `openspec/` | `root()` 第 42 行 |
| 文案来源：嵌套 JSON / HTML 内 JS 对象 | 两种格式都保留，由 `openspec/judge.yaml` 选 | `copy_config()` 第 62 行、`_flatten` 第 347 行、`extract_i18n` 第 356 行、`parse_copy` 第 371 行 |
| 叙事禁词（Divination 专属） | 移出引擎，改为项目配置 `banned` | `lint_copy` 第 281 行 |
| `chat` target（章字书有、Divination 无） | 保留 | `Target` 第 34 行 |
| 读配置：`settings` 对 `os.getenv` | 环境变量 → `~/.config/jev-judge/env`，不读项目 `.env` | `setting()` 第 75 行、`pick_provider` 第 196 行 |
| 复用连接与 `close()`（Divination 改进） | 采用 | `close` 第 226 行、`_jev` 第 231 行 |
| Risks 行接受两种写法（Divination 改进） | 采用 | `RISK_LINE` 第 273 行 |
| `report()` 不在推导式里做副作用（Divination 改进） | 采用 | `report` 第 389 行 |
| 人工模式下的 `--dry-run`（章字书做得对） | 采用章字书行为：带 `--dry-run` 时不走人工清单，没有 key 也能打印请求 | 第 242 行 |
| 文字差异 | 说明文字改为通用（不写任何项目路径） | 模块说明 |

新增（本 change 的需求）：通用规则 + 项目规则合并、同 id 覆盖（`load_rules` 第 139 行）；通用词表 + 项目词表（`lexicon` 第 317 行）；项目没有文案打分规则时长文案落 review（第 455 行，原先会抛 `StopIteration`）。

`ruff check src tests` 通过。注：同一时间另一个会话在本仓库工作区为 `lint/ruff-base.toml` 加了 F、E702、B、I 四组规则（change `ruff-base-more-rules`，未提交）；引擎按新规则也通过（修了一处 import 排序）。

### 1.3 通用规则与通用词表

- `base/judgments.yaml`：三条规则与章字书、Divination 的 `openspec/judgments.yaml` 中同 id 规则逐字相同（脚本比对，两边均 True）。
- `base/copy-lexicon.yaml`：17 个标签，均取自两个项目界面上实际出现、且不属于任何领域的标签（首页、当前位置、加载中…、加载失败、重试、知道了、收起、打开、关闭、选择、提交、搜索、全部、新对话、最近打开、共 {n} 条、第 {n} 张）。逐条过目：无书法或六爻领域词。

### 1.4 引擎测试

`judge/tests/test_engine.py` 36 条全部通过：在临时搭的接入项目里覆盖项目根判断、通用与项目规则合并与覆盖、规则校验、三段判定算数、两类 lint 与项目禁词、短标签与两份词表、目标文件、两种文案格式与配置缺项、key 读取顺序与不读项目 `.env`、无 key 的 dry-run、人工模式。

### 1.5 key 一处存放

`~/.config/jev-judge/env`（权限 600，目录 700）写入 key，从章字书 `api/.env` 复制，不经过任何输出。rules-layer 根目录 `jev-judge --change judge-engine`：Jev 判定，pass 4（本仓库无项目规则，只跑三条通用规则 + 产物格式 lint）。章字书 `api/` 下 `env -u TYPESAFE_API_KEY jev-judge --change adopt-shared-rules`：Jev 判定，pass 8（通用 3 条 + 四条红线 + lint）。本仓库 `git grep "TYPESAFE_API_KEY="` 只命中任务描述与测试里的假值。

与章字书原引擎相比，输出有两处预期内的差别，留待 2.4 对比时说明：通用规则先加载，`design-no-speculative-extension` 排到红线规则之前（只是显示顺序）；原章字书引擎没把 `lint/design` 的 pass 计入合计，合并后以 Divination 版为准计入，合计多 1。

## 2. 章字书迁移

在章字书分支 `chore/adopt-jev-judge` 上进行（先把另一个会话已完成的 `chore/ruff-base-v0.2` 快进合入 main；先归档 `adopt-shared-rules`，避免两个未归档 change 修改同一条 code-style 需求）。章字书提交 `0932630`。

### 2.1 章字书 change `adopt-jev-judge`

三份规格增量：code-style（Python 样板改为共享引擎）、judgment-rules（规则来源、key 位置、命令与文案配置）、chat-eval（实施时发现该规格也写着旧命令 `python -m app.ai.judge`，补进来）。`openspec validate --strict` 通过；用共享引擎跑 gates：pass 8 / block 0。

### 2.2 迁移前输出（`verification/zhangzishu-before/`）

ruff 通过；不联网测试 131 passed；Jev 回归 29 passed / 9 failed（9 条为已知的旧路径用例）；`--change archive/2026-10-28-portrait-fallback` 合计 pass 7；`--copy` 无待审文案。

### 2.3 改动

删 `api/app/ai/judge.py`；`pyproject.toml` 去掉 `judge` 依赖组、加可编辑路径依赖 `jev-judge`、删 `judge.py` 的 ruff 豁免；`config.py` 删 `typesafe_api_key`、`judge_provider`；`test_chat_eval.py` 改为 `from jev_judge import judge`，`settings.typesafe_api_key` 改为 `judge.api_key()`；`test_judge.py` 只留「本项目规则 enforces 有效」「本项目 design 过 lint」与 Jev 回归；新增 `openspec/judge.yaml`；`judgments.yaml` 删三条通用规则；词表删 15 个已进通用词表的标签；`CLAUDE.md` 命令表与样板、`api/README.md` 判断层用法改为 `jev-judge`。

实施中发现：章字书的 `Settings`（pydantic-settings）读 `api/.env`，默认不允许未声明的变量。删字段而 `.env` 仍有 `TYPESAFE_API_KEY` 会让 API 启动报错，所以把「删 `.env` 里的 key」从最后一步提前到与删字段同时做（key 已在 `~/.config/jev-judge/env`）。改后 `from app.main import app` 正常。

全仓 grep `typesafe_api_key`、`judge_provider`、`app.ai.judge`、`judge.settings`：只剩两份主规格（chat-eval、code-style）里的旧文字，由 `adopt-jev-judge` 的增量在归档时更新。

### 2.4 迁移前后对比（`verification/zhangzishu-after/`）

| 检查 | 迁移前 | 迁移后 | 说明 |
|---|---|---|---|
| ruff | 通过 | 通过 | |
| 不联网测试 | 131 passed | 112 passed | 少的 19 条是引擎测试，已在 rules-layer 覆盖（36 条） |
| Jev 回归 | 29 / 9 failed | 29 / 9 failed | 失败集合逐条相同 |
| `--change` 每条规则判定 | 8 条（含 lint） | 8 条 | 逐条相同；合计 pass 7 → 8 是因为共享引擎把 `lint/design` 计入合计（预期差别）；规则显示顺序不同（预期差别） |
| `--copy` | 无待审文案 | 无待审文案 | |
| 判断命令 | `python -m app.ai.judge` | `jev-judge`，裁判 jev | key 读自 `~/.config/jev-judge/env` |

### 2.5 key

`api/.env` 已无 `TYPESAFE_API_KEY`；`jev-judge` 仍以 jev 裁判运行。

注：`judge/pyproject.toml` 的包版本仍写 `0.2.0`，而引擎发布用的 tag 是 `v0.3.0`（编号因与 `ruff-base-more-rules` 撞号而后移）；下次打 tag 前把包版本改为与 tag 一致。

## 3. Divination 迁移

前提：Divination 已由另一个会话接入 rules-layer（#120，CI 钉 `v0.2.0`、软链，最近 3 次 CI success）。在分支 `chore/adopt-jev-judge` 上进行，PR #122。

### 3.1 Divination change `adopt-jev-judge`

三份规格增量：code-style（Python 样板）、judgment-rules（规则来源、key 位置、命令与文案配置；`I18N 块提取失败` 场景保留原名、内容改为 JSON5 解析位置——OpenSpec 不允许在 MODIFIED 中删改场景名）、copy-voice（叙事禁词改由 `openspec/judge.yaml` 配置）。用共享引擎跑 gates：pass 9 / block 0（五条红线均 pass）。核对 design 风险：CI 先检出 rules-layer 与软链、后装依赖；Render 只读 `requirements.txt`。

### 3.2 迁移前输出（`verification/divination-before/`）

ruff、ESLint 通过；不联网测试 689 通过；Jev 回归 30/30；`--change archive/2026-10-29-rules-layer`：8 pass / 1 review（`design-decisions-have-alternatives` p=0.55）；`--copy` 无待审文案。

### 3.3 改动

删 `backend/app/rules/judge.py` 与只为它存在的 `backend/app/rules/__init__.py`；新增 `openspec/judge.yaml`；`judgments.yaml` 删三条通用规则；词表删「知道了」「提交」；`requirements-dev.txt` 去掉 `typesafe-sdk`、`json5`，加 `-e ../../rules-layer/judge`；`ruff.toml` 删 `judge.py` 豁免；CI 两个 job 的 rules-layer 升到 `v0.3.0`；`test_judge.py` 只留本项目测试（enforces、用例对应规则、叙事禁词、本项目 design 过 lint、现网 I18N 可提取）与 Jev 回归；`CLAUDE.md`、`backend/README.md`、`.env.example` 改用 `jev-judge`；`backend/.env` 删 `TYPESAFE_API_KEY`、`JUDGE_PROVIDER` 两行（本机文件，不进仓库）。

实施中的失误：Divination 的 `.venv` 是 uv 建的、没有 pip，激活后 `pip install -r requirements-dev.txt` 实际用了 PATH 上 `miniforge3` 的 pip，把 51 个包装进了 miniforge base 环境（Python 3.13）。其中原本由 conda 管理且被覆盖的只有 `idna`（3.17 → 3.20）；其余 49 个无法区分是新装还是改了版本。已改用 `uv pip install --python .venv/bin/python -r requirements-dev.txt` 装进 Divination 自己的虚拟环境；base 环境如何恢复由用户决定。

### 3.4 迁移前后对比（`verification/divination-after/`）

| 检查 | 迁移前 | 迁移后 | 说明 |
|---|---|---|---|
| ruff / ESLint | 通过 | 通过 | |
| 不联网测试 | 689 | 667 | 少的 22 条是引擎测试，已在 rules-layer |
| Jev 回归 | 30/30 | 30/30 | |
| `--change` 每条判定 | 8 pass / 1 review | 相同 | review 那条 p=0.55 → 0.53，迁移前就是 review |
| `--copy` | 无待审文案 | 无待审文案 | |
