## MODIFIED Requirements

### Requirement: ruff 基础规则由项目继承

本仓库 SHALL 提供一份 ruff 基础配置：选用规则 ERA001（注释掉的代码）、T201（print）、BLE001（过宽 except）、C901（圈复杂度）、F（pyflakes：未用导入与变量、未定义名）、E702（一行用分号写多条语句）、B（bugbear：`zip` 不写 strict 等常见坑）、I（import 排序），复杂度上限 10。接入项目的 ruff 配置 SHALL 继承它，只写本项目的豁免路径与框架声明；每条豁免 MUST 写明原因，MUST NOT 在代码中逐行加 noqa。共享配置 MUST NOT 写任何项目的框架或领域名。

#### Scenario: 项目继承基础规则
- **WHEN** 在章字书 `api/` 或 Divination `backend/` 运行 ruff
- **THEN** 生效的选用规则与复杂度上限来自本仓库，项目配置里只出现豁免与框架声明

#### Scenario: 基础规则调整
- **WHEN** 本仓库的基础配置新增一条选用规则
- **THEN** 两个项目下次运行 ruff 即按新规则检查，项目配置不需要改

#### Scenario: 继承前后结果一致
- **WHEN** 两个项目从自带规则改为继承基础配置
- **THEN** 迁移前后 ruff 对同一份代码的报告完全相同

#### Scenario: 框架惯用写法的误报由项目声明
- **WHEN** 某项目的框架约定在参数默认值里调用函数（如 FastAPI 的 `Depends()`）而触发 B008
- **THEN** 该项目在自己的 ruff 配置里用 `extend-immutable-calls` 声明这些调用，共享配置不关闭 B008
