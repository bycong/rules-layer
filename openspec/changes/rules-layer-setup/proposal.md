# Proposal

## Why

规则共享了以后，新项目仍要照 Notion 手册一步步接入：写 `CLAUDE.md`、填 `config.yaml`、配 ruff / ESLint、写 gates，攒够三个 change 再装判断层。步骤多、容易漏，而且已经接入的项目没有办法知道自己和共享版本差了什么（`openspec/config.yaml` 不能引用外部文件，只能照写）。需要一个在项目根目录运行的 skill，按项目所处阶段做该做的事，并能反复运行做巡检。

本 change 是三步中的第三步，依赖 `shared-rules` 与 `judge-engine`。

## What Changes

- **skill `/rules-layer`**：放在本仓库，`~/.claude/skills/rules-layer` 软链接过来，在任何项目根目录可用。
- **识别项目**：语言、包管理（uv / pip / pnpm / npm）、有无前端及其形态、后端目录、有无 openspec、已归档 change 数、已装到哪一层。
- **按阶段做事**，可反复运行：
  - 阶段一（新项目）：引入代码规矩与 gates，写 `openspec/config.yaml` 的产物写法，配 ruff / ESLint 继承，补项目命令；红线向用户问，不代写。
  - 阶段二（1 到 2 个 change）：不装判断层，从已有方案中整理反复出现的问题，记成候选规则。
  - 阶段三（3 个以上 change）：装判断层，生成继承基础规则的 `judgments.yaml` 骨架与回归用例骨架，gates 启用判断步骤。
  - 已装好：只巡检，报告引入是否缺失、产物写法与共享版本的差异、项目是否仍有本该共享的副本，不自动改。
- 每次运行按手册的验证命令逐项检查，结果写进汇报。
- **试跑**：在 boyangcong（有 openspec、无 `CLAUDE.md`）跑阶段一；在章字书与 Divination 跑巡检。
- **Notion**：「新项目规则层搭建手册」开头加一句，说明步骤已做成 `/rules-layer`，并指向本仓库。
- 不做：替项目写红线或判断规则正文；skill 只生成骨架和候选，由人确认。
- 不做：巡检时自动修改项目文件，只报告。
- 不做：其他项目（Klarpix、Slidewand、yybu 等）的接入，留给 skill 跑通后逐个运行。
- 不做：Notion skill。Notion 继续放给人看的手册，skill 放本仓库。

## Capabilities

### New Capabilities

- `rules-layer-setup`：`/rules-layer` skill 对项目的识别、阶段判断、各阶段产出与巡检报告。

### Modified Capabilities

（无）

## Impact

- 新增：本仓库 `skills/rules-layer/`（`SKILL.md` 与模板片段）；`~/.claude/skills/rules-layer` 软链接。
- boyangcong：新增 `CLAUDE.md`，补全 `openspec/config.yaml`，加 ruff / ESLint 继承（视项目语言）。
- 章字书、Divination：只读巡检，不改文件。
- Notion：搭建手册开头加说明。
