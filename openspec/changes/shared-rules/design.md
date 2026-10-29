# Design

## Context

动机见 proposal.md「Why」，要求见 `specs/` 下四份规格。影响做法的现状与约束：

- 章字书（`zhangzishu`）：九条与 gates 写在根 `CLAUDE.md`，英文；ruff 规则在 `api/pyproject.toml` 的 `[tool.ruff.lint]`；ESLint 在 `web/eslint.config.mjs`（Next 规则 + 中文字面量规则）；code-style、copy-voice 是已归档的正式规格。
- Divination：九条与 gates 写在根 `CLAUDE.md`，中文；ruff 规则在 `backend/ruff.toml`；ESLint 在 `frontend/eslint.config.mjs`（`eslint-plugin-html`，复杂度棘轮 35）；code-style、copy-voice 规格在尚未归档的 `rules-layer` change 里。
- 两个项目的 `judge.py` 都只读本项目的 `openspec/copy-lexicon.yaml`，判断规则的档位描述写在本项目 `openspec/judgments.yaml`。本 change 不改 `judge.py`。
- 判断层按 `CLAUDE.md` 的二级标题检查 `enforces: L0/<标题>` 是否存在。
- OpenSpec 的 `config.yaml` 不能引用外部文件。
- 本仓库与所有项目都在 `~/AiDevelopProjects/` 下，互为兄弟目录。

## Goals / Non-Goals

**Goals:**
- 共享文件的目录与格式定下来，让项目只需一行引用或一行继承。
- 两个项目迁移前后，ruff、ESLint、判断 lint 的输出逐字相同；唯一允许变化的是章字书的文案打分，变化逐条报告。
- 本仓库自己先按共享规矩运行。

**Non-Goals:**
- 不改任何 `judge.py`；不建通用词表（见 `judge-engine`）。
- 不把共享配置发布成 npm 包或 Python 包。
- 不处理项目被单独 clone 到别处时的引用（只在巡检里报告缺失）。

## Decisions

### 1. 共享文件按读者分目录

```
rules-layer/
├── CLAUDE.md
├── rules/                 给 AI 与人读：code-style.md、python.md、workflow-gates.md、copy-voice.md
├── lint/                  给工具读：ruff-base.toml、eslint-base.mjs
└── openspec-base/         给项目照写：artifact-rules.yaml
```

`openspec-base/artifact-rules.yaml` 与项目 `config.yaml` 的 `rules:` 段格式完全一致，项目照写和巡检比对都是机械操作。

- 被否决：所有文件平铺在根目录。之后 `judge-engine` 要加 `judge/`、`rules-layer-setup` 要加 `skills/`，平铺会混在一起。
- 被否决：产物写法写成 Markdown。项目要照写进 YAML，Markdown 需要人工转换格式，巡检也无法逐行比对。

### 2. 项目用相对路径 `@../rules-layer/...` 引入

项目 `CLAUDE.md` 保留 `## Code style` 与 `## Workflow gates` 两个二级标题，标题下第一行是 `@../rules-layer/rules/<文件>`，之后写本项目补充：样板路径、语言落法位置、豁免说明；gates 下写「本项目命令表」（判断、ruff、测试、前端 lint、文案检查各一行）、实质类红线规则清单与额外步骤。共享的 `workflow-gates.md` 只按名称引用命令表的行（如「运行项目命令表的 ruff」），不写具体命令。

- 被否决：`@~/AiDevelopProjects/rules-layer/...`。项目搬目录时仍能找到，但 ruff 与 ESLint 的继承只能用相对路径，三处写法统一更不容易错。
- 被否决：把项目命令也写进共享文件，用占位符替换。Claude Code 的 `@` 引入不做变量替换，占位符会原样出现在上下文里。

### 3. 规矩正文统一用中文

合并时以 Divination 的中文版为底，对照章字书英文版逐条核对含义，章字书多出的说明（如 `.catch(() => …)` 示例）补进中文版。

- 被否决：英文。用户读中文、Notion 学习文档是中文、代码注释规定中文；中文版已在 Divination 实际运行一轮，没有出现执行偏差。

### 4. ruff 用 `extend` 继承，基础文件只放规则不放路径

`lint/ruff-base.toml` 只含 `select = ["ERA001", "T201", "BLE001", "C901"]` 与 `max-complexity = 10`。项目配置写 `extend = "<到 rules-layer 的相对路径>/lint/ruff-base.toml"`（章字书从 `api/` 起算，Divination 从 `backend/` 起算），只保留 `per-file-ignores`，不再写 `select`，以免覆盖基础规则。

- 被否决：项目保留 `select`，基础文件只当参考。改一处不能全生效，等于没有共享。
- 被否决：基础文件也放豁免路径。路径相对于哪个文件解析容易出错，且豁免本来就属于项目。

### 5. ESLint 基础规则只导出纯规则对象，不引插件

`lint/eslint-base.mjs` 导出一个规则对象：`no-console`、`no-nested-ternary` 为 error，`complexity` 为 `["error", 15]`。项目 `eslint.config.mjs` 用相对路径 import 后放进自己的配置块；Divination 在其后用自己的棘轮值覆盖 `complexity`。

- 被否决：基础文件导出完整配置（含 `eslint-plugin-html` 或 Next 规则）。插件会从本仓库目录解析，本仓库没有 `node_modules`，会直接报错；且两个项目的插件完全不同。

### 6. 先迁 Divination，再迁章字书

Divination 是共享版的来源，文案档位描述不变，迁移只改引用方式，行为风险最小；它的规格在未归档 change 里，可直接修改。章字书后迁：它的文案档位描述会变，需要重跑文案回归；两份已归档规格要在章字书仓库另开小 change 修改。

- 被否决：两个项目同时迁。同时出问题时无法判断是哪边引起的。

### 7. 迁移验证用「前后输出对比」

迁移前在每个项目把 ruff、ESLint、`judge --lint-only`（对一个已归档 change 与 `--copy`）的输出存成文件，迁移后再跑一次逐字比较。Divination 另跑一次 Jev 回归；章字书另跑文案回归，差异逐条列给用户。

- 被否决：只看退出码。退出码相同时报告内容仍可能不同（如少报一条豁免外的问题）。

### 8. 文案档位描述本 change 先手动同步

两个项目 `judgments.yaml` 的 `copy-voice` 规则，三档 `what` 文字手动改成与 `rules/copy-voice.md` 一字不差，例句不动。引擎能直接读共享描述之后（`judge-engine`），不再复制。

- 被否决：本 change 就改 `judge.py` 读共享文件。那是引擎改动，按 proposal 放在 `judge-engine`，本 change 不碰代码。

## Risks / Trade-offs

- [项目单独 clone 到别处时 `@../rules-layer` 找不到，AI 读不到九条] → 引入缺失在会话中可见；`rules-layer-setup` 巡检报告缺失；本 change 不处理这种情况
- [Claude Code 首次读项目外文件时弹确认框，未同意则规矩不生效] → 迁移每个项目后开一次会话确认已同意，并检查上下文含九条正文
- [章字书改用共享档位描述后文案打分口径变化] → 迁移后重跑文案回归，差异逐条报告由用户决定改期望还是调描述
- [ruff 项目配置残留 `select` 覆盖基础规则] → 迁移验证逐字比较输出；巡检检查项目配置不含 `select`
- [中文版合并时漏掉章字书英文版的某条细节] → 合并时逐条对照两版，差异列进 verification.md
- [产物写法照写进项目后再次分叉] → 规格要求只追加不改写；`rules-layer-setup` 巡检比对基础条目

## 改动文件与估计行数

| 位置 | 文件 | 估计 |
|---|---|---|
| rules-layer | `CLAUDE.md` | +40 |
| | `rules/code-style.md` | +25 |
| | `rules/python.md` | +10 |
| | `rules/workflow-gates.md` | +50 |
| | `rules/copy-voice.md` | +45 |
| | `openspec-base/artifact-rules.yaml` | +20 |
| | `lint/ruff-base.toml` | +8 |
| | `lint/eslint-base.mjs` | +15 |
| Divination | `CLAUDE.md` | −45 +20 |
| | `backend/ruff.toml` | −3 +2 |
| | `frontend/eslint.config.mjs` | −3 +3 |
| | `openspec/judgments.yaml` | ±3 |
| | `openspec/changes/rules-layer/specs/{code-style,copy-voice}/spec.md` | ±20 |
| 章字书 | `CLAUDE.md` | −40 +20 |
| | `api/pyproject.toml` | −4 +1 |
| | `web/eslint.config.mjs` | −3 +3 |
| | `openspec/judgments.yaml` | ±3 |
| | 新 change：code-style、copy-voice 规格增量 | +50 |

apply 后逐项对照，超出一倍的在完成汇报中说明原因。

## Migration Plan

1. rules-layer：写共享文件与本仓库 `CLAUDE.md`，提交。本仓库下一个 change 起按它执行。
2. Divination：存迁移前输出 → 改 `CLAUDE.md` 引用、ruff / ESLint 继承、`judgments.yaml` 档位描述、词表清理、未归档规格 → 对比输出、跑 Jev 回归 → 一个提交。
3. 章字书：在章字书开 change 改 code-style、copy-voice 两份规格 → 存迁移前输出 → 改 `CLAUDE.md`、ruff / ESLint、`judgments.yaml` → 对比输出、重跑文案回归并报告差异 → 一个提交。

回滚：每个项目的迁移是该项目仓库里的一个提交，出问题 `git revert` 该提交即恢复原状，不需要动 rules-layer。rules-layer 的提交与项目提交分开，回滚某个项目不影响另一个。
