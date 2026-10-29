## Why

共享 ruff 基础配置目前只有四条（ERA001、T201、BLE001、C901），只查得出九条里的第 6、8 条和复杂度。几类零误判、成本极低的问题一直没人查：没用到的 import 和变量、一行用分号写多条语句（正是九条附加条款「一行只做一件事」）、`zip` 不写 `strict`（长度不一致时静默丢数据）、import 顺序。2026-10-29 实测两个接入项目：Divination 50 处、章字书 54 处，其中 36 / 42 处可自动修。

## What Changes

- `lint/ruff-base.toml` 的 `select` 增加 `F`（pyflakes）、`E702`（分号多语句）、`B`（bugbear）、`I`（import 排序）。
- 规格 `shared-code-style` 的「ruff 基础规则由项目继承」改为列出八组规则，并补「框架惯用写法的误报由项目自己声明」场景。
- 两个接入项目各自清零：先 `ruff check --fix` 自动修，再手改其余；`zip` 补 `strict=True` 前逐处确认两边长度本应相等。
- 章字书在自己的 ruff 配置里用 `extend-immutable-calls` 声明 FastAPI 的 `Depends`、`Query` 等，消除 B008 误报。
- 打标签 `v0.2.0`；Divination CI 的 `ref` 从 `v0.1.0` 升到 `v0.2.0`。
- 不做：E501 行长（中文注释与长字符串，459 处全是噪音）。
- 不做：RUF（几乎全是「全角标点像英文标点」，中文项目全是误报）。
- 不做：PL 系列（魔法数字等，引擎里的法度常量会大量误报）。
- 不做：`ruff format` 统一格式化（Divination 77 个文件要重排，单独一个 change 决定）。
- 不做：ESLint 基础规则调整。

## Capabilities

### New Capabilities
<!-- 无 -->

### Modified Capabilities
- `shared-code-style`：ruff 基础规则从四条扩为八组；补框架误报由项目声明的场景。

## Impact

- 本仓库：`lint/ruff-base.toml`、`openspec/specs/shared-code-style/spec.md`（归档时同步）。
- 章字书：`api/` 下若干 Python 文件（自动修为主）、`api/pyproject.toml`（B008 声明）。
- Divination：`backend/` 下若干 Python 文件、`.github/workflows/ci.yml` 的 `ref`。
- 本地开发立即生效（两个项目读旁边的工作区）；Divination CI 在升 `ref` 后生效。
