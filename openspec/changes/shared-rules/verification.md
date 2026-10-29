# Verification

## 1. 共享文件

### 1.1 九条：中文版（Divination）与英文版（章字书）逐条对照

| 条 | 差异 | 共享版取法 |
|---|---|---|
| 开头 | 中文版写「前端：`frontend/CLAUDE.md`」与样板路径；英文版写 `web/CLAUDE.md` 与两个样板 | 去掉所有项目路径，改为「样板文件由项目在引入处写明」 |
| 1–7 | 含义一致 | 取中文版原文 |
| 8 | 中文版示例 `catch(e){}`；英文版示例 `.catch(() => …)` | 两个示例都保留 |
| 9 | 含义一致 | 取中文版原文 |
| 附加 | 「一行只做一件事」与 `a and b or c` 两版一致 | 取中文版原文 |

`grep -nE "api/|backend/|web/|frontend/" rules/code-style.md` 无输出；编号条目 9 条。

### 1.4 文案三档文字与 Divination 对照

0 档、1 档与 Divination `judgments.yaml` 逐字相同。2 档有一处有意的不同：Divination 原文的状态短句示例「排盘中」是六爻领域词，放进共享定义会出现在章字书的打分标准里，故换成通用的「加载中」。Divination 在 2.5 同步改成共享原文，并用 Jev 回归确认打分不变。

### 1.5 产物写法基础版

`openspec-base/artifact-rules.yaml` 首行加了一行说明注释（九条第 1 条），其余与章字书 `openspec/config.yaml` 的 `rules:` 段逐字相同：`diff <(sed -n '/^rules:/,$p' ../zhangzishu/openspec/config.yaml) <(grep -v '^#' openspec-base/artifact-rules.yaml)` 无输出。

### 1.6 lint 基础文件

- `uvx ruff check --config lint/ruff-base.toml --show-settings <探针文件>`：启用 ERA001、BLE001、T201、C901，`max_complexity = 10`；对含 `print` 与注释掉代码的探针文件报出 ERA001、T201。
- `node -e "import('./lint/eslint-base.mjs')..."`：打印 `no-console`、`no-nested-ternary`、`complexity`。

### 1.7 本仓库 CLAUDE.md 引入生效

在本仓库新开非交互会话 `claude -p`，要求不读文件、只凭上下文作答：
- 九条第 9 条原文：「9. 不加当前没有调用方的参数、配置项、扩展点。」与 `rules/code-style.md` 一致。
- 写完代码后第 1 步：「对本次改过的文件运行 `/simplify`。」与 `rules/workflow-gates.md` 一致。

本仓库的引入路径都在仓库内（`@rules/...`），不触发「项目外文件」确认框；项目引入 `@../rules-layer/...` 时才会触发。

## 2. Divination 迁移

### 2.1 迁移前输出（`verification/divination-before/`）

- `ruff.txt`：All checks passed；`eslint.txt`：退出码 0；`judge-change.txt`（`archive/2026-10-29-frontend-interaction-harness`，lint-only）：pass 1；`judge-copy.txt`：无待审文案。
- 因为检查结果本来就全部干净，「输出相同」证明力不够，另存了实际生效的配置：三个代表文件的完整 `ruff check --show-settings`，以及 `index.html`、`e2e/checklist.mjs` 的 ESLint 有效规则。
- Jev 回归基线：运行时 TypeSafe 不可达（直连与代理均 SSL EOF），30 条全部为 `TypeSafeAPIConnectionError`，没有一条是判断结果不符。网络恢复后补跑，见 2.5。

### 2.2 CLAUDE.md

`## Code style` 与 `## Workflow gates` 两个标题保留，正文换成 `@../rules-layer/...` 引入 + 本项目补充（样板、`__main__` 位置、命令表、五条红线、e2e 额外步骤）。「⭐ 学习文档同步 Notion」一节保留，开头注明它启用共享可选步骤。判断命令运行正常，未报 enforces 指向不存在。

### 2.3 ruff

`backend/ruff.toml` 删掉 `select` 与复杂度，加 `extend = "../../rules-layer/lint/ruff-base.toml"`，豁免原样保留。运行输出与迁移前逐字相同；三个代表文件的完整有效配置逐字相同（本地已无 `select`，有效规则仍在，证明继承生效）。

### 2.4 ESLint

`frontend/eslint.config.mjs` import 基础规则并展开进两个配置块；`index.html` 用棘轮值 35 覆盖复杂度，`e2e` 用 `"no-console": "off"`（清单脚本用 console 输出结果，是命令行边界）。lint 输出逐字相同；`index.html` 有效规则逐字相同；`e2e` 有效规则多出 `"no-console": 0`，即原来未设置、现在明确关闭，两者等价。

### 更正：Divination 词表没有照抄来的书法词

规划阶段用 `comm` 比对两份词表时命令写错，输出的其实是章字书自己的词，被误读为「两边共有」，进而得出「Divination 词表混入了章字书领域词」的结论，并写进了 copy-voice 规格场景、proposal、design、任务 2.5 与 Notion 第 03 篇。2.5 实施时逐词核实：「章字书」「书家」「无主碑帖」「拓片」「北齐」「墨迹」「重试」「收起」「关闭」在 Divination 词表中均为 0 次。已改正上述各处：规格场景改为「其他项目的领域词不进词表」，词表清理从任务中去掉。

### 2.5 文案档位文字

`openspec/judgments.yaml` 的 copy-voice 2 档文字改为共享版（「排盘中」→「加载中」），脚本比对三档与 `rules-layer/rules/copy-voice.md` 全部一字不差；注释改为指向共享标准。词表核实只含本项目的词，不改。不联网测试全部通过。Jev 回归（网络恢复后补跑）：迁移前（`git show HEAD:openspec/judgments.yaml` 临时还原）30/30 通过，迁移后 30/30 通过，失败清单前后都为空；结果见 `verification/divination-before/regression-full.txt` 与 `verification/divination-after-regression.txt`。

### 2.6 未归档规格

`openspec/changes/rules-layer/specs/` 下 code-style 与 copy-voice 改为：九条、Python 落法、三档定义以 `rules-layer` 为准，本项目规格只写样板、前端落法位置、lint 继承关系、例句、固定用语、叙事禁词与词表。`openspec validate rules-layer --strict` 通过。

### 2.7 引入生效

`claude -p` 非交互会话中，`@../rules-layer/...` 外部引入未被加载（模型回答「没有九条正文」）：非交互模式无法弹出外部引入确认框。需要在 Divination 打开一次交互会话并同意。

用户在 Divination 打开交互会话并同意外部引入后，再用 `claude -p` 验证：九条第 9 条与写完代码后第 1 步均按原文答出。Divination 提交 `4652751`（6 个文件；`docs/notion-drafts/` 下 3 个无关草稿未纳入）。

## 3. 章字书迁移

### 3.1 章字书 change `adopt-shared-rules`

proposal、design、tasks 与 code-style、copy-voice 两份 MODIFIED 增量；`openspec validate adopt-shared-rules --strict` 通过。章字书 gates：首次运行时 TypeSafe 不可达（连接错误三次），先跑 `--lint-only` 通过，等网络恢复后完整运行：pass 7 / review 0 / block 0（含四条红线与过度设计），之后才改章字书文件。

### 3.2 迁移前输出（`verification/zhangzishu-before/`）

ruff All checks passed；`pnpm lint` 退出码 0；判断 lint（`archive/2026-10-28-portrait-fallback`、`--copy`）均无问题；四个代表文件的完整 `--show-settings`；`gallery.tsx`、`types.ts` 的 ESLint 有效规则。Jev 回归基线 29 passed / 9 failed：9 条全是 `FileNotFoundError`，用例路径仍指向已归档前的 `openspec/changes/home-era-axis/` 与 `code-style/`，属迁移前就存在的问题，不在本 change 处理，只作为前后对比基线。

### 3.3 CLAUDE.md

英文 Code style 与 Workflow gates 正文换成 `@../rules-layer/...` 引入 + 本项目样板、命令表、四条红线（`design-no-runtime-yaml`、`design-no-deferred-infra`、`design-no-pages-for-unlisted`、`design-svg-canonical`）。补充文字保持英文，与该文件其余部分一致。判断命令运行正常。

### 3.4 ruff 与 ESLint

`api/pyproject.toml` 删 `[tool.ruff.lint] select` 与 `mccabe`，加 `[tool.ruff] extend`；`web/eslint.config.mjs` 全局规则块展开基础规则。ruff 输出、四个文件的完整有效配置、`pnpm lint` 输出、两个文件的 ESLint 有效规则，全部与迁移前逐字相同。

### 3.5 文案三档改为共享定义

三档描述换成共享原文后回归 24 passed / 14 failed：比基线多 5 条，均非误拦（4 条 review→pass，1 条 pass→review 且仅因置信 0.47 略低于 0.5）。逐条交用户，用户选择全部按建议改期望：

| 文案 | 原期望 | 共享定义下 | 新期望 |
|---|---|---|---|
| 加载中… | review | pass 0.99 | pass |
| 加载失败 | review | pass 0.88 | pass |
| 已复制链接到剪贴板。 | review | pass 0.96 | pass |
| 网络开小差了，请刷新页面重试 | review | pass 0.87 | pass |
| 可以先从书家与作品进入，逐字浏览和下载。 | pass | review（置信 0.47） | review |

改后回归 29 passed / 9 failed，失败集合与基线完全相同；不联网测试 131 passed。风险：最后一条置信 0.47 贴近门槛，Jev 波动时可能在 pass 与 review 间摇摆。

### 3.6 引入生效

用户在章字书打开交互会话同意外部引入后，`claude -p` 按原文答出九条第 9 条与写完代码后第 1 步。章字书提交 `5558265`（提交信息改为中文，与该仓库惯例一致）。

## 4. 收尾

### 4.1 估计行数与实际

| 位置 | 文件 | 估计 | 实际 | 说明 |
|---|---|---|---|---|
| rules-layer | `CLAUDE.md` | +40 | +43 | |
| | `rules/code-style.md` | +25 | +15 | |
| | `rules/python.md` | +10 | +9 | |
| | `rules/workflow-gates.md` | +50 | +42 | |
| | `rules/copy-voice.md` | +45 | +43 | |
| | `openspec-base/artifact-rules.yaml` | +20 | +15 | |
| | `lint/ruff-base.toml` | +8 | +7 | |
| | `lint/eslint-base.mjs` | +15 | +8 | |
| Divination | `CLAUDE.md` | −45 +20 | −39 +26 | |
| | `backend/ruff.toml` | −3 +2 | −7 +2 | 删除超出一倍：除 `select` 外还删了 `[lint]`、`[lint.mccabe]` 两个表头与空行 |
| | `frontend/eslint.config.mjs` | −3 +3 | −7 +11 | 超出一倍：/simplify 把两块重复的基础规则与空 catch 豁免抽成本地常量 |
| | `openspec/judgments.yaml` | ±3 | ±2 | |
| | 未归档规格 | ±20 | ±10 | |
| 章字书 | `CLAUDE.md` | −40 +20 | −38 +22 | |
| | `api/pyproject.toml` | −4 +1 | −5 +2 | |
| | `web/eslint.config.mjs` | −3 +3 | −4 +3 | |
| | `openspec/judgments.yaml` | ±3 | ±4 | |
| | `adopt-shared-rules` 规格增量 | +50 | +62 | design、proposal、tasks 另有 +100，估计时只算了规格 |
| | `api/tests/judge_cases.yaml` | 未估计 | ±10 | 回归差异经用户决定改期望，计划外 |

### 4.2 写完代码后的检查

1. `/simplify`：对本 change 改过的 6 个 lint 配置跑四路审查（复用、精简、效率、层级）。采纳 2 条：章字书 ESLint 注释不再重复列出基础规则内容、「前端取 15」的理由挪到 `eslint-base.mjs`；Divination ESLint 两块共用的基础规则与空 catch 豁免抽成本地常量。跳过 2 条（不在本次改动的行内）：章字书 ESLint 脚手架留下的英文注释；Divination `ruff.toml` 第 7 行「同上」不准确、第 14 行「本 change」会过时。效率方面无发现。改后两个项目 lint 输出与有效配置与改前一致。提交：Divination `bf4e39b`、章字书 `00490dd`。
2. ruff：两个项目输出与迁移前逐字相同（3.4、2.3）。
3. 测试：Divination 不联网全部通过、Jev 回归 30/30；章字书不联网 131 passed、Jev 回归失败集合与基线相同。
4. 前端 lint：两个项目输出与迁移前逐字相同。
5. 文案检查：两个项目 `--copy --lint-only` 无待审文案（本次没有改界面文案文件）。
6. 额外步骤：Divination 的 e2e 交互回归跳过，本次没有改 `frontend/index.html`；rules-layer 的额外步骤（改了 `lint/` 后在两个项目复核）即上面第 1、4 条。

## 5. 上线前发现：CI 找不到 rules-layer

Divination 的 CI（`.github/workflows/ci.yml`）在仓库内跑 `ruff check` 与 `npm run lint`，只检出本仓库；迁移后两者分别通过 `extend` 与 import 依赖 `../rules-layer`，在 CI 上会直接报错。design 只把「项目单独 clone 时 CLAUDE.md 读不到正文」列为不处理，漏了 CI 这种后果更重的情况。章字书没有 CI，所以没暴露。

处理：rules-layer 建为公开仓库 https://github.com/bycong/rules-layer ，tag `v0.1.0`（推送前把检查输出里的本机绝对路径换成 `~`，并改写了尚未推送的历史，历史中不再含本机路径）。Divination 的迁移提交在本地分支 `chore/adopt-rules-layer` 上，等 CI 接好 rules-layer 后再推。design 的 Risks 已补上这一条。
