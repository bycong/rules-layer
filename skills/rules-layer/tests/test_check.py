"""check.py 的测试：在临时 git 仓库里搭出各种接入状态，核对识别、各层状态、巡检与下一阶段。基础文件取本仓库真实的那一份。
运行（本仓库根目录）：uv run --with pytest --with pyyaml pytest skills/rules-layer/tests
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SPEC = importlib.util.spec_from_file_location("check", Path(__file__).parents[1] / "check.py")
check = importlib.util.module_from_spec(SPEC)
sys.modules["check"] = check                                # dataclass 解析注解时要在 sys.modules 里找到本模块
SPEC.loader.exec_module(check)

BASE_RULES = yaml.safe_load(check.BASE_ARTIFACTS.read_text(encoding="utf-8"))["rules"]
BASE_JUDGMENTS = yaml.safe_load(check.BASE_JUDGMENTS.read_text(encoding="utf-8"))

CLAUDE_OK = """# x

## Code style

@../rules-layer/rules/code-style.md

## Workflow gates

@../rules-layer/rules/workflow-gates.md
"""


# ---------- 1. 临时项目 ----------

def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _commit(root: Path) -> None:
    _git(root, "add", "-A")
    _git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")


def _run(root: Path, monkeypatch) -> tuple[check.Report, str]:
    monkeypatch.chdir(root)
    files = check.tracked(root)
    report = check.Report()
    check.identify(root, files, report)
    check.layers(root, files, report)
    check.audit(root, files, report)
    return report, check.next_stage(root, report)


def _archive(root: Path, n: int) -> None:
    for i in range(n):
        _write(root, f"openspec/changes/archive/2026-01-0{i + 1}-c{i}/proposal.md", "# P\n")


@pytest.fixture
def bare(tmp_path):
    """只有 openspec 与一份 Python 代码、什么都没接入的项目。"""
    root = tmp_path / "proj"
    _write(root, "openspec/config.yaml", "schema: spec-driven\ncontext: 项目\n")
    _write(root, "app/main.py", "x = 1\n")
    _git(root, "init", "-q", "-b", "main")
    _commit(root)
    return root


@pytest.fixture
def joined(bare):
    """阶段一已装好的项目。"""
    _write(bare, "CLAUDE.md", CLAUDE_OK)
    _write(bare, "openspec/config.yaml", yaml.safe_dump({"schema": "spec-driven", "context": "项目", "rules": BASE_RULES}, allow_unicode=True))
    _write(bare, "ruff.toml", 'extend = "../rules-layer/lint/ruff-base.toml"\n')
    _commit(bare)
    return bare


# ---------- 2. 下一阶段 ----------

def test_not_in_git_returns_none(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert check.project_root() is None


def test_bare_project_starts_at_stage_one_even_with_history(bare, monkeypatch):
    _archive(bare, 5)
    _commit(bare)
    report, stage = _run(bare, monkeypatch)
    assert stage == "阶段一"
    assert "没有 CLAUDE.md" in report.layers["阶段一 代码规矩与 gates"]
    assert "有 Python 代码但没有 ruff 配置" in report.layers["阶段一 lint 继承"]


def test_joined_with_few_archives_waits_for_more(joined, monkeypatch):
    _archive(joined, 2)
    _commit(joined)
    _, stage = _run(joined, monkeypatch)
    assert stage.startswith("阶段二") and "还差 1 个" in stage


def test_joined_with_enough_archives_can_go_to_stage_three(joined, monkeypatch):
    _archive(joined, 3)
    _commit(joined)
    _, stage = _run(joined, monkeypatch)
    assert stage.startswith("阶段二") and "可进入阶段三" in stage


def test_fully_installed_goes_to_audit(joined, monkeypatch):
    _write(joined, "openspec/judgments.yaml", "[]\n")
    _commit(joined)
    _, stage = _run(joined, monkeypatch)
    assert stage == "巡检"


# ---------- 3. 各层状态 ----------

def test_claude_without_import_is_missing(joined, monkeypatch):
    _write(joined, "CLAUDE.md", "# x\n\n## Code style\n\n九条正文\n\n## Workflow gates\n\n@../rules-layer/rules/workflow-gates.md\n")
    report, stage = _run(joined, monkeypatch)
    assert any("code-style.md" in m for m in report.layers["阶段一 代码规矩与 gates"])
    assert stage == "阶段一"


def test_ruff_with_select_is_reported(joined, monkeypatch):
    _write(joined, "ruff.toml", 'extend = "../rules-layer/lint/ruff-base.toml"\n[lint]\nselect = ["E"]\n')
    _commit(joined)
    report, _ = _run(joined, monkeypatch)
    assert any("select" in m for m in report.layers["阶段一 lint 继承"])


def test_eslint_without_base_is_reported(joined, monkeypatch):
    _write(joined, "web/eslint.config.mjs", "export default [];\n")
    _commit(joined)
    report, _ = _run(joined, monkeypatch)
    assert any("eslint-base.mjs" in m for m in report.layers["阶段一 lint 继承"])


# ---------- 4. 巡检 ----------

def _finding(report: check.Report, name: str) -> list[str]:
    return dict(report.findings)[name]


def test_rewritten_base_rule_is_a_finding_appended_is_not(joined, monkeypatch):
    rules = {k: list(v) for k, v in BASE_RULES.items()}
    rules["design"][1] = rules["design"][1] + "（本项目另有说明）"     # 改写
    rules["tasks"].append("本项目追加的一条")                          # 追加
    _write(joined, "openspec/config.yaml", yaml.safe_dump({"schema": "spec-driven", "rules": rules}, allow_unicode=True))
    _commit(joined)
    report, stage = _run(joined, monkeypatch)
    diff = _finding(report, "产物写法与基础版的差异")
    assert len(diff) == 1 and diff[0].startswith("rules.design")
    assert stage != "阶段一"


def test_engine_copy_is_reported(joined, monkeypatch):
    _write(joined, "backend/judge.py", "def load_rules():\n    return []\n")
    _commit(joined)
    report, _ = _run(joined, monkeypatch)
    assert _finding(report, "判断引擎副本") == ["backend/judge.py"]


def test_identical_base_rule_is_duplicate_override_is_not(joined, monkeypatch):
    same = BASE_JUDGMENTS[0]
    changed = dict(BASE_JUDGMENTS[1], question="收紧版")
    _write(joined, "openspec/judgments.yaml", yaml.safe_dump([same, changed], allow_unicode=True))
    _commit(joined)
    report, _ = _run(joined, monkeypatch)
    assert _finding(report, "与通用规则重复的项目规则") == [same["id"]]


def test_generic_words_in_project_lexicon(joined, monkeypatch):
    _write(joined, "openspec/copy-lexicon.yaml", "labels:\n  - 重试\n  - 书家\n")
    _commit(joined)
    report, _ = _run(joined, monkeypatch)
    assert _finding(report, "项目词表中已在通用词表的词") == ["重试"]


def _ci(root: Path, ref: str) -> None:
    _write(root, ".github/workflows/ci.yml", f"jobs:\n  a:\n    steps:\n      - uses: actions/checkout@v4\n        with:\n          repository: bycong/rules-layer\n          ref: {ref}\n          path: rules-layer\n")
    _commit(root)


def test_ci_pinned_to_old_tag_is_reported(joined, monkeypatch):
    _ci(joined, "v0.1.0")
    report, _ = _run(joined, monkeypatch)
    behind = _finding(report, "CI 钉的 rules-layer 版本")
    assert len(behind) == 1 and "v0.1.0" in behind[0] and check.latest_tag() in behind[0]


def test_ci_pinned_to_latest_is_fine(joined, monkeypatch):
    _ci(joined, check.latest_tag())
    report, _ = _run(joined, monkeypatch)
    assert _finding(report, "CI 钉的 rules-layer 版本") == []
    assert dict(report.facts)["CI"].endswith(check.latest_tag())


def test_uncommitted_new_files_are_seen(bare, monkeypatch):
    _write(bare, "ruff.toml", 'extend = "../rules-layer/lint/ruff-base.toml"\n')      # 新建未提交
    report, _ = _run(bare, monkeypatch)
    assert report.layers["阶段一 lint 继承"] == []


def test_check_is_read_only(joined, monkeypatch):
    before = subprocess.run(["git", "status", "--porcelain"], cwd=joined, capture_output=True, text=True).stdout
    _run(joined, monkeypatch)
    after = subprocess.run(["git", "status", "--porcelain"], cwd=joined, capture_output=True, text=True).stdout
    assert before == after
