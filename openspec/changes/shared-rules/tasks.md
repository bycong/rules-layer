# Tasks

## 1. rules-layer：共享文件与本仓库 CLAUDE.md

- [x] 1.1 写 `rules/code-style.md`：以 Divination 中文九条与附加条款为底，逐条对照章字书英文版，把英文版多出的说明（如 `.catch(() => …)` 示例）补进中文版，不写任何项目路径。验证：九条与「一行只做一件事」都在；两版差异逐条记入 `verification.md`；`grep -nE "api/|backend/|web/|frontend/" rules/code-style.md` 无输出。
- [x] 1.2 写 `rules/python.md`：章节分隔线格式、`if __name__ == "__main__"` 只放脚本与命令行入口、测试放 tests 目录、机械部分交给 ruff、豁免写在配置里并注明原因。验证：五点都在；`grep -nE "api/|backend/|pipeline/" rules/python.md` 无输出。
- [x] 1.3 写 `rules/workflow-gates.md`：三个检查点、格式类与实质类 block 的处理、写完代码后六步顺序与逐项汇报、未装判断层时只跑不依赖 Jev 的步骤、可选的 Notion 阶段学习文档步骤；命令一律写成「项目命令表的〈名称〉」。验证：`grep -nE "uv run|pnpm|npm |\.venv|PYTHONPATH" rules/workflow-gates.md` 无输出；对照 `specs/workflow-gates/spec.md` 七条需求逐条能找到对应段落。
- [x] 1.4 写 `rules/copy-voice.md`：三档定义（取 Divination `judgments.yaml` 三条 `what` 原文，2 档里的领域词「排盘中」换成通用的「加载中」）、通用禁用、报错与空状态写法、只润色不重写、新增须达 2 档、项目词表只收本项目的词、标注校准方法。验证：用脚本比对本文件三档文字与 Divination `judgments.yaml` 的三条 `what`，只有「排盘中→加载中」一处不同。
- [x] 1.5 写 `openspec-base/artifact-rules.yaml`：取章字书 `openspec/config.yaml` 的 `rules:` 段。验证：`diff <(sed -n '/^rules:/,$p' ../zhangzishu/openspec/config.yaml) openspec-base/artifact-rules.yaml` 无差异。
- [x] 1.6 写 `lint/ruff-base.toml`（只含 select 与复杂度 10）与 `lint/eslint-base.mjs`（只导出 `no-console`、`no-nested-ternary`、`complexity: 15` 规则对象，不 import 任何包）。验证：`uvx ruff check --config lint/ruff-base.toml --show-settings .` 能解析并显示四条规则；`node -e "import('./lint/eslint-base.mjs').then(m=>console.log(Object.keys(m.default ?? m)))"` 打印三条规则名。
- [x] 1.7 写本仓库 `CLAUDE.md`：项目简介、`## Code style` 与 `## Workflow gates` 两个标题下引入共享文件；命令表写明判断层未装、暂借章字书 judge 跑通用规则的命令；启用 Notion 学习文档步骤，落点为 rules-layer 项目页。验证：在本仓库新开 Claude Code 会话，确认上下文含九条与 gates 正文（问「第 9 条是什么」能答出原文）。
- [x] 1.8 建 `openspec/changes/shared-rules/verification.md`（1.1 的差异表、后续各组的前后对比结果都记在这里），提交本仓库。验证：`git log --oneline` 有该提交，`git status` 干净。

## 2. Divination 迁移

- [x] 2.1 存迁移前输出到本 change 目录下的 `verification/divination-before/`：`ruff check app scripts tools tests`、`npm --prefix ../frontend run lint`、`python -m app.rules.judge --change <一个已归档 change> --lint-only`、`python -m app.rules.judge --copy --lint-only`。验证：四个输出文件都在且非空（或记录「无输出」）。
- [x] 2.2 改 `CLAUDE.md`：`## Code style` 与 `## Workflow gates` 下的正文换成引入 + 本项目补充（样板路径、前端落法位置、命令表、五条红线、额外步骤：前端交互回归）；「⭐ 学习文档同步 Notion」一节改为启用共享可选步骤并写明落点，保留它特有的「04 · Tasks 展开」要求。验证：两个二级标题仍在；运行任一 judge 命令不报 enforces 指向不存在。
- [x] 2.3 改 `backend/ruff.toml`：加 `extend` 指向 `../../rules-layer/lint/ruff-base.toml`，删掉 `select` 与复杂度，保留全部豁免。验证：重跑 2.1 的 ruff 命令，输出与迁移前逐字相同。
- [x] 2.4 改 `frontend/eslint.config.mjs`：import 基础规则放进 `index.html` 与 `e2e` 两个配置块，`complexity` 仍用各自原值（35 与 15）覆盖。验证：重跑 lint，输出与迁移前逐字相同。
- [x] 2.5 改 `openspec/judgments.yaml` 的 copy-voice 三条 `what` 为共享原文（只有 2 档「排盘中」改为「加载中」）；核实 `openspec/copy-lexicon.yaml` 只含本项目的词（已核实：36 条均为六爻界面标签，无其他项目领域词，不改）。验证：重跑两条 `--lint-only` 命令与迁移前相同；`pytest -q -k regression` 全部通过且与迁移前结果一致。
- [x] 2.6 改未归档 `openspec/changes/rules-layer/specs/` 下的 code-style 与 copy-voice：规矩正文所在位置改为 rules-layer，项目规格只写本项目补充。验证：`openspec validate rules-layer --strict` 通过。
- [x] 2.7 在 Divination 新开 Claude Code 会话，同意外部引入确认框，确认上下文含九条与 gates 正文；提交 Divination。验证：会话中问「写完代码后第一步做什么」答出 `/simplify`；`git log` 有该提交；对比结果记入 `verification.md`。

## 3. 章字书迁移

- [x] 3.1 在章字书开 change `adopt-shared-rules`：code-style、copy-voice 两份规格的 MODIFIED 增量（规矩正文位置改为 rules-layer；copy-voice 档位描述引用共享标准）；按章字书 gates 对 proposal 跑 judge。验证：`openspec validate adopt-shared-rules --strict` 通过；judge 无 block。
- [x] 3.2 存迁移前输出到本 change 目录下的 `verification/zhangzishu-before/`：`uv run ruff check app ../pipeline`、`pnpm -C ../web lint`、`judge --change <一个已归档 change> --lint-only`、`judge --copy --lint-only`，并跑一次文案回归存结果。验证：输出文件都在。
- [x] 3.3 改 `CLAUDE.md`：英文 Code style 与 gates 正文换成引入 + 本项目补充（样板路径、`web/CLAUDE.md` 位置、命令表、四条红线）。验证：两个二级标题仍在；judge 不报 enforces 指向不存在。
- [x] 3.4 改 `api/pyproject.toml` 加 `extend`、删 `select` 与复杂度；改 `web/eslint.config.mjs` import 基础规则，保留 Next 与中文字面量规则。验证：ruff 与 lint 输出与迁移前逐字相同。
- [x] 3.5 改 `openspec/judgments.yaml` 的 copy-voice 三条 `what` 为共享原文（例句不动），重跑文案回归。验证：与 3.2 的结果对比，变化的条目逐条列给用户，按用户决定改期望或调描述后回归全部通过。
- [x] 3.6 在章字书新开会话确认引入生效；提交章字书。验证：会话中能答出九条第 9 条原文；`git log` 有该提交；对比结果记入 `verification.md`。

## 4. 收尾核对

- [x] 4.1 对照 design「改动文件与估计行数」逐项记录实际行数，超出一倍的写明原因。验证：`verification.md` 有完整对照表。
- [x] 4.2 按本仓库 gates 跑写完代码后的检查：对本 change 改过的配置与脚本文件跑 `/simplify`，其余不适用的步骤写明跳过原因。验证：完成汇报逐项列出结果。

## Workflow follow-up

- 归档本 change（`/opsx:archive shared-rules`），四份规格进入 `openspec/specs/`。
- 归档章字书的 `adopt-shared-rules`。
- 在 Notion rules-layer 项目页写下一篇编号学习文档。
- 开始 `judge-engine` 的 specs。
