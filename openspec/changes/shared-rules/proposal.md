# Proposal

## Why

规则层（代码规矩 + Jev 判断闸门）目前靠「照 Notion 手册在每个项目抄一遍」落地。第二个项目 Divination 抄完不到一周就分叉了：Code style 九条一份英文、一份中文，措辞各自改过；文案三档标准 Divination 校准时补了「文气做作也算 1 档」，章字书没有；Workflow gates 结构相同、Divination 多出一步；`openspec/config.yaml` 的 rules 只差一句兼容说明。这违反了规则层的第一原则「每条规矩只住一处」。趁只有两个项目落地、合并成本最低，把这些文字类规矩收回本仓库。

本 change 是三步中的第一步，只收文字与配置；判断引擎见 `judge-engine`，搭建巡检 skill 见 `rules-layer-setup`。

## What Changes

- **代码规矩**：九条（不分语言）与 Python 落法各成一份文件；ruff 一份基础配置，ESLint 一份两边共有的基础规则（`no-console`、`no-nested-ternary`、复杂度目标 15）。项目 `CLAUDE.md` 保留 `## Code style` 标题，标题下用 `@` 引入共享文件，只补本项目样板路径与豁免；ruff / ESLint 继承基础配置，只写自己的豁免与复杂度棘轮。前端落法暂不共享：React 落法只有章字书在用，单文件原生 JS 落法只有 Divination 在用，各留原处，出现第二个同类项目时再收。
- **界面文案规范**：三档（模板 / 生硬 / 自然）的定义与尺度、通用禁用（感叹号、颜文字、英文感叹词）、报错与空状态的写法、「1 档改 2 档只润色不重写」、新增文案须达 2 档、短标签查词表的规则（项目词表只收本项目的词）、双人标注的校准方法。通用词表与「两份词表一起查」放到 `judge-engine`，因为现有 `judge.py` 只读项目词表，提前移走通用词会让它们全部落 review。档位定义采用 Divination 2026-10-28 校准后的版本（1 档含「文气做作」）。项目只写领域例句（Jev 打分准确率取决于例句）、本站固定用语、项目词表与禁词这类红线。只管界面文案，方案文档怎么写由产物写法管。
- **Workflow gates**：三个检查点（方案写完、写代码前、写完代码后）各做什么、block 与 review 怎么处理、完成汇报要逐项写结果，写成共享文件供 `CLAUDE.md` 引入。写完代码后的检查点按顺序：`/simplify` 精简改过的文件 → ruff 机械检查 → 不联网测试（改了判断规则或模型版本才加跑回归）→ 改了前端跑前端 lint → 改了界面文案跑文案检查 → 逐项汇报，跳过的写明原因。具体命令、红线规则清单和项目额外步骤（如 Divination 的前端交互回归）留在项目。
  - 可选步骤：每完成一个阶段，把过程整理成零基础学习文档同步到 Notion；项目在自己的 `CLAUDE.md` 写明 Notion 落点才启用。
- **产物写法（L1）**：`openspec/config.yaml` 的 rules 共享基础版一份。OpenSpec 配置不能引用外部文件，所以由项目照共享版写入，差异交给 `rules-layer-setup` 的巡检发现。
- **本仓库自用**：新建本仓库的 `CLAUDE.md`，引入上述共享规矩与 gates，本仓库之后的 change 按它执行。
- **迁移两个已落地项目的文字部分**：章字书与 Divination 的 Code style 正文、gates 正文、ruff 基础规则、文案标准中的共享部分改为引用；Divination 词表清掉照抄带入的书法领域词。判断命令本次不动，仍用各自的 `judge.py`；两个项目判断规则中的文案档位描述先手动改成共享版文字。规矩正文统一用中文。
- 不做：判断引擎的合并与迁移（`judge-engine` 做）。
- 不做：搭建巡检 skill 与新项目试跑（`rules-layer-setup` 做）。
- 不做：其他项目（Klarpix、Slidewand、yybu 等）的接入。
- 不做：用户级 `~/.claude/CLAUDE.md` 或 `~/AiDevelopProjects/CLAUDE.md` 自动生效，避免规矩带进 multica、agency-agents 这类别人的仓库。
- 不做：重新校准两个项目的文案阈值，各自保留当前阈值与例句；不审繁体与英文文案。
- 不做：前端交互回归的共享。现在只有 Divination 在用，等第二个项目需要时再抽。
- 不做：Codex `AGENTS.md` 同步、CI、pre-push 钩子。

## Capabilities

### New Capabilities

- `shared-code-style`：代码写法规矩（九条与 Python 落法）及 ruff / ESLint 基础配置的唯一版本，以及项目引用它们的方式。
- `copy-voice`：界面文案的档位标准、通用禁用、短标签查词表的规则与校准方法的共享基础，以及项目在其上补充例句、固定用语、词表与禁词的方式。名称与两个项目现有规格一致。
- `workflow-gates`：三个检查点的步骤与处理规则（含写完代码后的 `/simplify`、ruff、测试、前端 lint、文案检查、逐项汇报），项目补充命令与额外步骤的方式，以及可选的 Notion 学习文档步骤。
- `artifact-rules`：OpenSpec 产物（proposal / design / specs / tasks）写法规则的共享基础版。

### Modified Capabilities

（无。本仓库新建，尚无既有规格。）

## Impact

- 新增：本仓库 `CLAUDE.md`、代码规矩与落法文件、ruff / ESLint 基础配置、文案标准、gates 文件、产物写法基础版。
- 章字书：`CLAUDE.md` 改为引用（`web/CLAUDE.md` 的 React 落法不动）；`api/pyproject.toml` 与 `web/eslint.config.mjs` 改为继承；`openspec/judgments.yaml` 的文案档位描述改为共享版文字并重跑文案回归；code-style 与 copy-voice 两份已归档规格改为引用共享标准（在章字书侧另开 change）。
- Divination：`CLAUDE.md` 改为引用（`frontend/CLAUDE.md` 的单文件落法不动）；`backend/ruff.toml` 与 `frontend/eslint.config.mjs` 改为继承；`openspec/copy-lexicon.yaml` 清掉书法领域词；`openspec/judgments.yaml` 的文案档位描述改为共享版文字；尚未归档的 `rules-layer` change 中的 code-style 与 copy-voice 规格改为引用共享标准。
- 两个项目的 `CLAUDE.md` 读取 `@../rules-layer/...`，依赖本仓库与项目处于同一父目录。
