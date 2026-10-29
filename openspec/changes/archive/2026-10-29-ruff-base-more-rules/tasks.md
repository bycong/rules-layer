## 1. 共享配置

- [x] 1.1 `lint/ruff-base.toml` 的 `select` 加 `F`、`E702`、`B`、`I`，注释写明每组查什么。验证：`uvx ruff check --config lint/ruff-base.toml --show-settings .` 列出八组。

## 2. 章字书清零

- [x] 2.1 `api/pyproject.toml` 加 `[tool.ruff.lint.flake8-bugbear] extend-immutable-calls`，声明 FastAPI 的 `Depends`、`Query`、`Path`、`Body` 等，注明原因。验证：`uv run ruff check app ../pipeline tests --select B008` 无输出。
- [x] 2.2 `uv run ruff check app ../pipeline tests --fix` 自动修，再手改 B905、E702、F811 等剩余项。验证：`uv run ruff check app ../pipeline tests` 打印 All checks passed!；`uv run python -m pytest tests -q -k "not regression"` 全过。
- [x] 2.3 章字书新开分支提交。验证：`git log` 有该提交。

## 3. Divination 清零

- [x] 3.1 在 `chore/adopt-rules-layer` 之上新开分支，`ruff check app scripts tools tests --fix` 自动修，再手改 B905、B007、E702、F841。验证：ruff 通过；`PYTHONPATH=. pytest -q -k "not regression"` 全过。
- [x] 3.2 B905 逐处确认长度本应相等后补 `strict=True`；确为有意截断的写 `strict=False` 并注释。验证：每处在完成汇报中列出判断。

## 4. 发版与升级

- [x] 4.1 本仓库提交、打标签 `v0.2.0`、推送。验证：`git ls-remote --tags origin` 有 `v0.2.0`。
- [x] 4.2 Divination `.github/workflows/ci.yml` 两处 `ref: v0.1.0` 改为 `v0.2.0`，与 3.1 同一分支提交，推送并开 PR（叠在 #120 上）。验证：PR 的 CI 两项通过。
