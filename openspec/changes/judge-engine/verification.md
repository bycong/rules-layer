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
