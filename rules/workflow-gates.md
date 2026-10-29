<!-- 三个自动检查点：包住每个 OpenSpec change，各项目在 CLAUDE.md 的「## Workflow gates」下用 @ 引入 -->

这些检查点包住每一个 OpenSpec change，自动执行，无需提醒。写在 CLAUDE.md 体系里而不是 `.claude/commands/opsx/*.md`，因为 `openspec update` 会重新生成那些文件。

下文的「命令表的〈名称〉」指项目 CLAUDE.md 在本节引入处写的「本项目命令表」中那一行；「红线规则」指项目在同处列出的实质类规则；「额外步骤」同理。

**项目未装判断层时**：只执行「写完代码后」中不依赖 Jev 的步骤（`/simplify`、ruff、测试、前端 lint、额外步骤），方案写完与写代码前两个检查点不执行判断，汇报中写明「判断层未装」。

## 方案刚写完时

经 `/opsx:continue`、`/opsx:ff`、`/opsx:propose`，或 explore 模式手写出 proposal / design 之后：

1. 运行命令表的「判断」。
2. 格式类 block（`lint/design`、`proposal-states-non-goals`、`design-decisions-have-alternatives`）是起草失误：自己改好产物再跑一次。
3. 实质类 block 或 review（项目列出的红线规则，以及 `design-no-speculative-extension`）等于改方案：报告给用户决定，不自行修改。
4. 把最终结果（和改了什么）附在给用户的方案汇报里。

## apply 写任何代码之前

产物可能已被用户改过；用户已经看过，所以这里不静默修改。

1. 运行命令表的「判断」。
2. 任一 block：停下不碰代码，逐条报告规则与原文，等用户决定。
3. 只有 review：用一小段列出来，然后继续。

## apply 最后一个任务做完、汇报完成之前

按顺序：

1. 对本次改过的文件运行 `/simplify`。
2. 运行命令表的「ruff」，修掉报出的问题后重跑直到通过。
3. 运行命令表的「测试」（不联网部分）；若改了判断规则文件或 `JEV_MODEL`，加跑 Jev 回归。
4. 若改了前端，运行命令表的「前端 lint」并修掉问题。
5. 若改了界面文案，运行命令表的「文案检查」：block 必须修，review 列出。
6. 运行项目列出的额外步骤。
7. 完成汇报里逐项写每一步的结果，含跳过了什么、为什么。

## 可选：阶段学习文档同步 Notion

项目 CLAUDE.md 写明 Notion 落点页面才启用；没写就不启用，汇报中也不提。

启用后，每完成一个阶段（一个产物写完，或一段 apply 完成），主动在落点下新建下一篇编号子页，无需用户提醒。写给零基础读者：做了什么、为什么这样做、要敲的命令、应该看到什么；注明仓库是权威记录。
