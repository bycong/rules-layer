# Proposal

## Why

规则共享了以后，新项目仍要照 Notion 手册一步步接入：写 `CLAUDE.md`、填 `config.yaml`、配 ruff / ESLint、写 gates，攒够三个 change 再装判断层。步骤多、容易漏，而且已经接入的项目没有办法知道自己和共享版本差了什么（`openspec/config.yaml` 不能引用外部文件，只能照写）。需要一个在项目根目录运行的 skill，按项目所处阶段做该做的事，并能反复运行做巡检。

本 change 是三步中的第三步，`shared-rules` 与 `judge-engine` 均已归档（rules-layer `v0.3.1`），章字书与 Divination 已全部接入。

## What Changes

- **skill `/rules-layer`**：放在本仓库，`~/.claude/skills/rules-layer` 软链接过来，在任何项目根目录可用。
- **识别项目**：语言、包管理（uv / pip / pnpm / npm）、有无前端及其形态、后端目录、有无 openspec、已归档 change 数、已装到哪一层。
- **按安装状态做事**，可反复运行，每次只补第一个缺的阶段，动手前列出要改的文件并等用户确认（归档数只决定判断层能否安装，不决定从哪开始：boyangcong 已归档 5 个，但连阶段一都没装）：
  - 阶段一：引入代码规矩与 gates，写 `openspec/config.yaml` 的产物写法，配 ruff / ESLint 继承，补项目命令表；红线向用户问，不代写。
  - 阶段二：从已归档方案中整理反复出现的问题，作为候选判断规则列在汇报里；不足 3 个归档时说明还差几个。
  - 阶段三（已归档至少 3 个且用户确认了规则）：生成只含项目规则的 `judgments.yaml`、`judge.yaml`、回归用例骨架，命令表改用 `jev-judge`；缺命令或 key 时给步骤，不代填 key。
  - 已装好：只巡检并报告——引入缺失、产物写法与共享版本的差异、lint 配置未继承、项目里残留的引擎副本、与通用规则重复的项目规则、已进通用词表的项目词、CI 钉的 rules-layer 版本落后于最新 tag。
- 每次运行按手册的验证命令逐项检查，结果写进汇报。
- **试跑**：在 boyangcong（有 openspec、无 `CLAUDE.md`）跑阶段一；在章字书与 Divination 跑巡检。
- **Notion**：「新项目规则层搭建手册」开头加一句，说明步骤已做成 `/rules-layer`，并指向本仓库。
- 不做：替项目写红线或判断规则正文；skill 只生成骨架和候选，由人确认。
- 不做：巡检时自动修改项目文件，只报告。
- 不做：git 提交或推送；工作区有用户未提交的改动时只碰本阶段负责的文件。
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
