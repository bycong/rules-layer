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
