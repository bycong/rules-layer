## Context

`lint/ruff-base.toml` 由章字书 `api/pyproject.toml` 与 Divination `backend/ruff.toml` 用 `extend` 继承；本地读旁边的 rules-layer 工作区，Divination CI 检出固定标签 `v0.1.0`。两个项目都是 FastAPI 后端：章字书用 `Depends()` 作参数默认值（8 处），Divination 不用。2026-10-29 加 `--extend-select F,E702,B,I` 实测：

| 规则 | Divination | 章字书 |
| --- | --- | --- |
| I001 | 21 | 39 |
| F401 / F541 | 15 | 3 |
| F841 / F811 | 1 | 1 |
| E702 | 5 | 1 |
| B905 | 6 | 2 |
| B007 | 2 | 0 |
| B008 | 0 | 8 |

## Goals / Non-Goals

**Goals:**
- 基础配置多查四组零误判的问题，两个项目同一天清零。
- 共享仓库不写任何项目的框架或路径；框架惯用写法的豁免由项目声明。

**Non-Goals:**
- E501、RUF、PL、`ruff format`、ESLint 调整（见 proposal）。

## Decisions

**1. 选 F、E702、B、I 四组，不选 E 全组。**
F 抓未用导入与未定义名，B 抓 `zip` 截断等常见坑，E702 是「一行一件事」的机械检查，I 全部可自动修。备选是开 E 全组：否决，E501 行长在中文项目里 459 处全是噪音，E 组其他规则价值低。

**2. B008（默认参数里调函数）留在基础配置，FastAPI 的 `Depends` 等由章字书用 `extend-immutable-calls` 声明。**
B008 对普通代码有用（可变默认值是真坑）；FastAPI 的 `Depends()` 是框架约定，属于项目知识。备选是基础配置直接 `ignore = ["B008"]`：否决，一个项目的框架习惯不该让所有项目失去这条检查。备选是基础配置写 `extend-immutable-calls = ["fastapi.Depends"]`：否决，违反「共享文件不写项目领域词」。

**3. B905 一律补 `strict=True`，逐处确认长度本应相等；确为有意截断的写 `strict=False` 并注释原因。**
备选是全部写 `strict=False` 求快：否决，等于把检查关掉，失去发现「两列数据长度不一致」的机会。

**4. 先改共享配置、两个项目本地清零，再打标签升 CI。**
本地两个项目读工作区，改了 base 当场生效，可以立即量清零结果；CI 钉标签，升 `ref` 与清零改动同一个提交，CI 不会出现「规则新、代码旧」的红灯。备选是先打标签再清零：否决，标签发出到项目升级之间 Divination 的 CI 本来就看旧标签，无收益。

## 改动文件与估计行数

| 文件 | 动作 | 估计行数 |
| --- | --- | --- |
| `lint/ruff-base.toml` | select 加四组 | ±2 |
| `openspec/specs/shared-code-style/spec.md` | 改一条需求、加一个场景 | +8 |
| 章字书 `api/**/*.py` | 自动修 42 处 + 手改约 4 处 | ±60 |
| 章字书 `api/pyproject.toml` | B008 声明 | +3 |
| Divination `backend/**/*.py` | 自动修 36 处 + 手改约 14 处 | ±70 |
| Divination `.github/workflows/ci.yml` | ref 升级 | ±2 |

## Risks / Trade-offs

- [补 `strict=True` 后某处长度其实不等，运行时抛 ValueError] → 逐处读上下文确认；两个项目的测试全跑；确为有意截断的显式写 `strict=False`。
- [import 自动排序改变了有副作用的导入顺序] → 跑全部测试；Divination `scripts/` 里 `sys.path.insert` 之后的导入已有 `# noqa: E402`，排序不跨越它。
- [删掉「未用导入」其实被外部按名字引用（再导出）] → 自动修前看 F401 清单，`__init__.py` 里的再导出改为 `__all__` 或保留并在配置中豁免。
- [Divination 的 #120 还没合并，CI 仍看 v0.1.0] → 本 change 的 Divination 部分叠在 #120 上开 PR，合并顺序写进 PR。

## Migration Plan

顺序：改 `lint/ruff-base.toml` → 章字书清零并提交 → Divination 清零 → 本仓库打 `v0.2.0` 并推送 → Divination 升 CI `ref` 并开 PR。回滚：`ruff-base.toml` 去掉四组并打 `v0.2.1`（或项目把 `ref` 退回 `v0.1.0`）；两个项目的清零改动都是等价改写，可以保留。
