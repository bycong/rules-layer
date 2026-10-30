# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""规则层识别与巡检：只读，输出识别表、各层状态、巡检结果，最后一行是下一阶段。/rules-layer skill 先跑它再动手。

用法（在接入项目内任意目录）：
    uv run --script ~/AiDevelopProjects/rules-layer/skills/rules-layer/check.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

RULES = Path(__file__).resolve().parents[2]                 # 本仓库根：软链接解析后的真实位置
BASE_JUDGMENTS = RULES / "judge/src/jev_judge/base/judgments.yaml"
BASE_LEXICON = RULES / "judge/src/jev_judge/base/copy-lexicon.yaml"
BASE_ARTIFACTS = RULES / "openspec-base/artifact-rules.yaml"
SHARED_PATHS = ["rules", "lint", "openspec-base", "judge/src"]   # 项目会用到的共享部分，比对 CI 版本差异时只看这些
MIN_ARCHIVED = 3                                            # 判断层至少要这么多已归档 change 作测试用例


@dataclass
class Report:
    facts: list[tuple[str, str]] = field(default_factory=list)       # 识别表
    layers: dict[str, list[str]] = field(default_factory=dict)       # 层名 → 缺失项；空表示已装好
    findings: list[tuple[str, list[str]]] = field(default_factory=list)   # 巡检项 → 偏离；空表示一致


# ---------- 1. 读项目 ----------

def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True).stdout


def tracked(root: Path) -> list[str]:
    """已跟踪的文件，加上未被 .gitignore 忽略的新文件（skill 不提交，刚写的文件也要看得到）；虚拟环境与依赖目录靠 .gitignore 排除。"""
    return git(root, "ls-files", "--cached", "--others", "--exclude-standard").splitlines()


def _yaml(path: Path, default):
    if not path.exists():
        return default
    return yaml.safe_load(path.read_text(encoding="utf-8")) or default


def _dirs_with(files: list[str], names: tuple[str, ...]) -> list[str]:
    hits = {str(Path(f).parent) for f in files if Path(f).name in names}
    return sorted(hits)


def identify(root: Path, files: list[str], report: Report) -> None:
    """识别表：语言与包管理、目录、openspec、归档数、CI、未提交改动。"""
    # 1. 语言与包管理
    managers = [m for m, lock in (("uv", "uv.lock"), ("pip", "requirements.txt"), ("pnpm", "pnpm-lock.yaml"), ("npm", "package-lock.json"))
                if any(Path(f).name == lock for f in files)]
    has_py = any(f.endswith(".py") for f in files)
    has_js = any(Path(f).name == "package.json" for f in files)
    langs = [name for name, ok in (("Python", has_py), ("JS/TS", has_js)) if ok]
    report.facts.append(("语言", "、".join(langs) or "未识别"))
    report.facts.append(("包管理", "、".join(managers) or "无锁文件"))

    # 2. 目录
    report.facts.append(("Python 目录", "、".join(_dirs_with(files, ("pyproject.toml", "requirements.txt"))) or "—"))
    report.facts.append(("前端目录", "、".join(_dirs_with(files, ("package.json",))) or "—"))

    # 3. openspec、CI、工作区
    report.facts.append(("已归档 change", str(archived(root))))
    refs = ci_refs(root, files)
    report.facts.append(("CI", "、".join(f"{f} 钉 {r}" for f, r in refs) if refs else ("有，未引用 rules-layer" if ci_files(files) else "无")))
    dirty = len(git(root, "status", "--porcelain").splitlines())
    report.facts.append(("未提交改动", f"{dirty} 个文件" if dirty else "无"))


def archived(root: Path) -> int:
    d = root / "openspec/changes/archive"
    return sum(1 for p in d.iterdir() if p.is_dir()) if d.is_dir() else 0


def ci_files(files: list[str]) -> list[str]:
    return [f for f in files if f.startswith(".github/workflows/") and f.endswith((".yml", ".yaml"))]


def ci_refs(root: Path, files: list[str]) -> list[tuple[str, str]]:
    """CI 里检出 bycong/rules-layer 时钉的 ref，返回 (工作流文件, ref) 列表；同一文件多处只记一次。"""
    out: list[tuple[str, str]] = []
    for f in ci_files(files):
        text = (root / f).read_text(encoding="utf-8")
        for m in re.finditer(r"repository:\s*bycong/rules-layer\s*\n\s*ref:\s*(\S+)", text):
            if (f, m.group(1)) not in out:
                out.append((f, m.group(1)))
    return out


# ---------- 2. 各层状态 ----------

def check_claude(root: Path) -> list[str]:
    """阶段一的 CLAUDE.md：两个标题下各有对 rules-layer 的引入。返回缺失项，空表示齐全。"""
    path = root / "CLAUDE.md"
    if not path.exists():
        return ["没有 CLAUDE.md"]
    text = path.read_text(encoding="utf-8")
    missing = []
    for head, ref in (("Code style", "rules/code-style.md"), ("Workflow gates", "rules/workflow-gates.md")):
        section = re.search(rf"^##\s+{head}.*?$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
        if section is None:
            missing.append(f"CLAUDE.md 没有「## {head}」")
        elif f"@../rules-layer/{ref}" not in section.group(1):
            missing.append(f"「## {head}」下没有引入 ../rules-layer/{ref}")
    return missing


def project_artifact_rules(root: Path) -> dict:
    return _yaml(root / "openspec/config.yaml", {}).get("rules") or {}


def artifact_rules_diff(root: Path) -> list[str]:
    """项目 config.yaml 的 rules 是否包含基础版每一条（一字不差）；项目追加的条目不算偏离。"""
    base = _yaml(BASE_ARTIFACTS, {}).get("rules") or {}
    project = project_artifact_rules(root)
    if not project:
        # 走到这里说明整段 rules 都没有，已记为阶段一未装，不再逐条重复
        return []
    missing = []
    for artifact, items in base.items():
        have = project.get(artifact) or []
        missing += [f"rules.{artifact} 缺少或改写了：{item[:30]}…" for item in items if item not in have]
    return missing


def ruff_configs(root: Path, files: list[str]) -> list[tuple[str, str]]:
    """(文件, 内容) 列表：ruff.toml，以及含 [tool.ruff] 的 pyproject.toml。"""
    out = []
    for f in files:
        name = Path(f).name
        if name not in ("ruff.toml", "pyproject.toml"):
            continue
        text = (root / f).read_text(encoding="utf-8")
        if name == "ruff.toml" or "[tool.ruff" in text:
            out.append((f, text))
    return out


def check_lint(root: Path, files: list[str]) -> list[str]:
    """ruff 继承基础配置且不写 select；ESLint 引入基础规则。只检查项目实际有的语言。"""
    problems = []
    configs = ruff_configs(root, files)
    if any(f.endswith(".py") for f in files) and not configs:
        problems.append("有 Python 代码但没有 ruff 配置")
    for f, text in configs:
        if "rules-layer/lint/ruff-base.toml" not in text:
            problems.append(f"{f} 没有 extend rules-layer 的 ruff-base.toml")
        if re.search(r"^\s*select\s*=", text, re.M):
            problems.append(f"{f} 仍写 select，会覆盖基础规则")
    for f in files:
        if Path(f).name.startswith("eslint.config.") and "rules-layer/lint/eslint-base.mjs" not in (root / f).read_text(encoding="utf-8"):
            problems.append(f"{f} 没有引入 rules-layer 的 eslint-base.mjs")
    return problems


def layers(root: Path, files: list[str], report: Report) -> None:
    report.layers["阶段一 代码规矩与 gates"] = check_claude(root)
    # 产物写法只看有没有 rules 段；有但与基础版不一致是巡检发现，不是没装
    report.layers["阶段一 产物写法"] = [] if project_artifact_rules(root) else ["openspec/config.yaml 没有 rules 段"]
    report.layers["阶段一 lint 继承"] = check_lint(root, files)
    report.layers["阶段三 判断层"] = [] if (root / "openspec/judgments.yaml").exists() else ["没有 openspec/judgments.yaml"]


# ---------- 3. 巡检：本该共享的副本与版本 ----------

def engine_copies(root: Path, files: list[str]) -> list[str]:
    """项目里定义了 load_rules 的 .py 文件，视为判断引擎副本。"""
    return [f for f in files if f.endswith(".py") and "def load_rules" in (root / f).read_text(encoding="utf-8", errors="ignore")]


def duplicate_rules(root: Path) -> list[str]:
    """项目规则中与通用规则同 id 且内容完全相同的条目；同 id 不同内容是有意覆盖，不算。"""
    base = {r["id"]: r for r in _yaml(BASE_JUDGMENTS, [])}
    return [r["id"] for r in _yaml(root / "openspec/judgments.yaml", []) if base.get(r["id"]) == r]


def lexicon_overlap(root: Path) -> list[str]:
    base = set(_yaml(BASE_LEXICON, {}).get("labels") or [])
    project = _yaml(root / "openspec/copy-lexicon.yaml", {}).get("labels") or []
    return [w for w in project if w in base]


def latest_tag() -> str | None:
    tags = git(RULES, "tag", "--list", "v*", "--sort=-v:refname").split()
    return tags[0] if tags else None


def ci_behind(root: Path, files: list[str]) -> list[str]:
    """CI 钉的 rules-layer 版本早于最新 tag 时，列出两版之间改过的共享文件。"""
    latest = latest_tag()
    out = []
    for f, ref in ci_refs(root, files):
        if latest is None or ref == latest:
            continue
        changed = git(RULES, "diff", "--name-only", ref, latest, "--", *SHARED_PATHS).split()
        out.append(f"{f} 钉 {ref}，最新 {latest}；共享文件改动：{('、'.join(changed) or '无')}")
    return out


def audit(root: Path, files: list[str], report: Report) -> None:
    report.findings.append(("产物写法与基础版的差异", artifact_rules_diff(root)))
    report.findings.append(("判断引擎副本", engine_copies(root, files)))
    report.findings.append(("与通用规则重复的项目规则", duplicate_rules(root)))
    report.findings.append(("项目词表中已在通用词表的词", lexicon_overlap(root)))
    report.findings.append(("CI 钉的 rules-layer 版本", ci_behind(root, files)))


# ---------- 4. 下一阶段 ----------

def next_stage(root: Path, report: Report) -> str:
    """一 / 二 / 巡检。阶段三要用户确认规则，脚本只说明能否进入。"""
    stage_one = [k for k in report.layers if k.startswith("阶段一")]
    if any(report.layers[k] for k in stage_one):
        return "阶段一"
    if report.layers["阶段三 判断层"]:
        n = archived(root)
        if n < MIN_ARCHIVED:
            return f"阶段二（已归档 {n} 个，装判断层还差 {MIN_ARCHIVED - n} 个）"
        return f"阶段二（已归档 {n} 个，用户确认候选规则后可进入阶段三）"
    return "巡检"


# ---------- 5. 跑 ----------

def project_root() -> Path | None:
    """当前目录所在 git 仓库的根；不在 git 仓库里返回 None。"""
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return Path(out.stdout.strip()) if out.returncode == 0 else None


def render(root: Path, report: Report, stage: str) -> str:
    lines = [f"# 规则层识别：{root.name}", "", "## 识别表"]
    lines += [f"- {k}：{v}" for k, v in report.facts]
    lines += ["", "## 各层状态"]
    for name, missing in report.layers.items():
        lines.append(f"- {name}：{'已装好' if not missing else '缺'}")
        lines += [f"  - {m}" for m in missing]
    lines += ["", "## 巡检"]
    for name, items in report.findings:
        lines.append(f"- {name}：{'一致' if not items else ''}")
        lines += [f"  - {i}" for i in items]
    lines += ["", f"下一阶段：{stage}"]
    return "\n".join(lines)


def main() -> int:
    # 1. 项目根与 openspec；不满足就停，不做其他检查
    root = project_root()
    if root is None:
        print("下一阶段：先在 git 仓库里运行（当前目录不在 git 仓库）")
        return 1
    if not (root / "openspec").is_dir():
        print(f"# 规则层识别：{root.name}\n\n没有 openspec/。\n\n下一阶段：先 openspec init")
        return 1

    # 2. 识别、各层、巡检
    files = tracked(root)
    report = Report()
    identify(root, files, report)
    layers(root, files, report)
    audit(root, files, report)
    print(render(root, report, next_stage(root, report)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
