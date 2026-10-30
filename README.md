# rules-layer

AiDevelopProjects 下各项目共用的规则层：代码规矩、Workflow gates、界面文案标准、OpenSpec 产物写法、ruff / ESLint 基础配置、Jev 判断引擎 `jev-judge`，以及给项目接入与巡检用的 `/rules-layer` skill。共享的只在这里一份，项目通过 `@` 引入、ruff `extend`、ESLint import、可编辑依赖引用，不复制。

## 目录

| 目录 | 内容 |
|---|---|
| `rules/` | 给 AI 与人读的规矩：`code-style.md`、`python.md`、`workflow-gates.md`、`copy-voice.md` |
| `lint/` | `ruff-base.toml`、`eslint-base.mjs` |
| `openspec-base/` | 产物写法基础版 `artifact-rules.yaml`，项目照写进 `openspec/config.yaml` |
| `judge/` | 判断引擎包 `jev-judge`（命令与库），含三条通用判断规则与通用短标签词表 |
| `skills/rules-layer/` | `/rules-layer` skill：`SKILL.md`、只读识别与巡检脚本 `check.py`、模板 |
| `openspec/` | 本仓库自己的 change 与规格 |

本仓库要放在项目的同级目录（`~/AiDevelopProjects/rules-layer`），项目里的 `../rules-layer/...` 引用才找得到。

## 安装（每台机器一次）

```bash
# 1. /rules-layer skill
ln -s ~/AiDevelopProjects/rules-layer/skills/rules-layer ~/.claude/skills/rules-layer

# 2. 判断引擎命令 jev-judge（可编辑安装，改了源码立即生效）
uv tool install -e ~/AiDevelopProjects/rules-layer/judge

# 3. Jev 的 key，只放这一处，不进任何仓库
mkdir -p ~/.config/jev-judge && chmod 700 ~/.config/jev-judge
printf 'TYPESAFE_API_KEY=〈你的 key〉\n' > ~/.config/jev-judge/env && chmod 600 ~/.config/jev-judge/env

# 4. 本仓库是公开的：启用提交前钩子，拦截本机绝对路径
git -C ~/AiDevelopProjects/rules-layer config core.hooksPath .githooks
```

## 给项目接入或巡检

在项目根目录让 Claude Code 运行 `/rules-layer`。它先跑 `check.py` 识别项目与各层状态，再补上下一个未装的阶段（代码规矩与 gates → 候选判断规则 → 判断层）；已装好的项目只巡检并报告偏离。动手前会列出要改的文件等你确认，不会提交。

只想看识别与巡检结果：

```bash
uv run -q --script ~/AiDevelopProjects/rules-layer/skills/rules-layer/check.py
```

接入后第一次在该项目开交互会话时，Claude Code 会询问是否允许读取项目外文件（`@../rules-layer/...`），选同意。

## CI

项目 CI 要检出本仓库并放到工作目录的上一级，钉一个 tag：

```yaml
- uses: actions/checkout@v4
  with:
    repository: bycong/rules-layer
    ref: v0.3.1
    path: rules-layer
- run: ln -s "$GITHUB_WORKSPACE/rules-layer" "$GITHUB_WORKSPACE/../rules-layer"
```

升级共享规则时改 `ref`，并先在项目里跑一遍 lint 与测试。
