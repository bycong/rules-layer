"""引擎测试：在临时搭的接入项目里跑，不联网、不依赖任何真实项目。各项目的 Jev 回归用例留在项目里。
运行：cd judge && uv run pytest
"""
import json
import subprocess
from pathlib import Path

import pytest

from jev_judge import judge
from jev_judge.judge import verdict

PROJECT_RULE = """
- id: design-no-yaml
  target: design
  enforces: L1/context
  type: noul
  question: 该设计最终采纳的方案是：运行时直接读 YAML
  expect: false
  thresholds: { pass: 0.7, block: 0.3 }

- id: copy-voice
  target: copy
  enforces: L1/context
  type: score
  question: 这条界面文案的语气属于哪一档
  levels: [模板, 生硬, 自然]
  thresholds: { pass: 0.75, block: 0.25, min_confidence: 0.5 }
"""


# ---------- 1. 临时接入项目 ----------

def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def project(tmp_path, monkeypatch):
    """一个最小的接入项目：git 仓库、CLAUDE.md、openspec 配置与项目规则，当前目录切到它的子目录。"""
    root = tmp_path / "proj"
    _write(root, "CLAUDE.md", "# x\n\n## Code style\n\n九条\n")
    _write(root, "openspec/config.yaml", "context: 项目\nrules:\n  proposal: [a]\n  design: [b]\n")
    _write(root, "openspec/judgments.yaml", PROJECT_RULE)
    _write(root, "openspec/copy-lexicon.yaml", "labels:\n  - 待收录\n")
    _write(root, "api/README.md", "子目录\n")
    _git(root, "init", "-q", "-b", "main")
    _git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "init")
    monkeypatch.chdir(root / "api")
    monkeypatch.setattr(judge, "USER_ENV", tmp_path / "no-such-env")
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    monkeypatch.delenv("JUDGE_PROVIDER", raising=False)
    judge.root.cache_clear()
    judge.config.cache_clear()
    yield root
    judge.root.cache_clear()
    judge.config.cache_clear()


def _commit_all(root: Path) -> None:
    _git(root, "add", "-A")
    _git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "x")


# ---------- 2. 项目根 ----------

def test_root_is_git_toplevel_from_subdir(project):
    assert judge.root() == project.resolve()


def test_outside_git_exits(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    judge.root.cache_clear()
    with pytest.raises(SystemExit) as e:
        judge.root()
    assert "git" in str(e.value)


def test_git_repo_without_openspec_exits(tmp_path, monkeypatch):
    _git(tmp_path, "init", "-q")
    monkeypatch.chdir(tmp_path)
    judge.root.cache_clear()
    with pytest.raises(SystemExit) as e:
        judge.root()
    assert "openspec" in str(e.value)


# ---------- 3. 规则：通用 + 项目 ----------

def test_base_rules_load_with_project_rules(project):
    ids = [r.id for r in judge.load_rules()]
    assert ids[:3] == ["proposal-states-non-goals", "design-decisions-have-alternatives", "design-no-speculative-extension"]
    assert "design-no-yaml" in ids


def test_project_rule_overrides_base_by_id(project):
    _write(project, "openspec/judgments.yaml", PROJECT_RULE + """
- id: design-decisions-have-alternatives
  target: design
  enforces: L1/design
  type: noul
  question: 收紧版
  expect: true
  thresholds: { pass: 0.7, block: 0.5 }
""")
    rules = {r.id: r for r in judge.load_rules()}
    assert rules["design-decisions-have-alternatives"].thresholds.block == 0.5
    assert [r.id for r in judge.load_rules()].count("design-decisions-have-alternatives") == 1


def test_project_without_rules_file_uses_base_only(project):
    (project / "openspec/judgments.yaml").unlink()
    assert len(judge.load_rules()) == 3


def _load_bad(project: Path, body: str) -> str:
    _write(project, "openspec/judgments.yaml", body)
    with pytest.raises(SystemExit) as e:
        judge.load_rules()
    return str(e.value)


def test_rule_without_enforces_is_rejected(project):
    msg = _load_bad(project, "- {id: x, target: design, type: noul, question: q, expect: true, thresholds: {pass: 0.7, block: 0.3}}")
    assert "'x'" in msg


def test_choice_type_is_rejected(project):
    msg = _load_bad(project, "- {id: y, target: design, enforces: L1/design, type: choice, question: q, thresholds: {pass: 0.7, block: 0.3}}")
    assert "'y'" in msg


def test_dangling_enforces_is_rejected(project):
    msg = _load_bad(project, "- {id: z, target: design, enforces: specs/no-such-spec, type: noul, question: q, expect: true, thresholds: {pass: 0.7, block: 0.3}}")
    assert "z" in msg and "specs/no-such-spec" in msg


# ---------- 4. 三段判定的算数 ----------

def _rules(project) -> dict:
    return {r.id: r for r in judge.load_rules()}


def test_noul_expect_false_flips(project):
    rule = _rules(project)["design-no-yaml"]
    assert verdict(rule, 0.02, None) == ("pass", "p=0.98")
    assert verdict(rule, 0.95, None)[0] == "block"


def test_thresholds_boundaries_inclusive_pass_exclusive_block(project):
    rule = _rules(project)["design-no-yaml"]                       # pass 0.7 / block 0.3
    assert verdict(rule, 0.30, None)[0] == "pass"                  # p = 0.70 等于 pass 阈值算 pass
    assert verdict(rule, 0.70, None)[0] == "review"                # p = 0.30 等于 block 阈值不算 block
    assert verdict(rule, 0.71, None)[0] == "block"


def test_score_normalizes_and_checks_confidence(project):
    rule = _rules(project)["copy-voice"]
    assert verdict(rule, 1.96, 0.93)[0] == "pass"
    assert verdict(rule, 1.0, 0.9)[0] == "review"
    assert verdict(rule, 0.02, 0.95)[0] == "block"
    v, why = verdict(rule, 0.91, 0.14)
    assert v == "review" and "置信度不足" in why


def test_alternatives_rule_never_blocks(project):
    rule = _rules(project)["design-decisions-have-alternatives"]    # 通用版 block 阈值为 0
    assert verdict(rule, 0.08, None)[0] == "review"


# ---------- 5. lint ----------

@pytest.mark.parametrize("text", ["操作失败!", "操作失败！", "出错了 :(", "Oops! 出错了"])
def test_copy_lint_blocks_banned(project, text):
    assert judge.lint_copy(text)


def test_copy_lint_blocks_project_words(project):
    _write(project, "openspec/judge.yaml", "banned: [保证应验]\n")
    assert judge.lint_copy("此卦保证应验") == "含项目禁词「保证应验」"
    assert judge.lint_copy("服务暂时没有响应，可以稍后重试。") is None


DESIGN_OK = "## Risks / Trade-offs\n\n- [字体体积大] → 子集化\n\n## Migration Plan\n\n随 PR 发布。回滚即回退该 PR。\n"


def test_design_lint_ok():
    assert judge.lint_design(DESIGN_OK) == []
    assert judge.lint_design(DESIGN_OK.replace("[字体体积大]", "**字体体积大**")) == []


def test_design_lint_catches_bad_risk_line_and_missing_rollback():
    bad = DESIGN_OK.replace("- [字体体积大] → 子集化", "- 字体体积大，要子集化").replace("回滚即回退该 PR。", "")
    problems = judge.lint_design(bad)
    assert any("Risks" in p for p in problems) and any("回滚" in p for p in problems)


# ---------- 6. 短标签与词表 ----------

def test_label_len_ignores_placeholders():
    assert judge.label_len("前 {y}") == 1
    assert judge.label_len("已收录 {live} / 共 {total} 人") > judge.SHORT_LABEL


def test_lexicon_is_base_plus_project(project):
    labels = judge.lexicon()
    assert {"重试", "关闭"} <= labels                              # 通用
    assert "待收录" in labels                                       # 项目


# ---------- 7. 目标文件 ----------

def test_missing_design_is_skipped_not_error(project, capsys):
    _write(project, "openspec/changes/archive/2026-01-01-x/proposal.md", "# P\n")
    files = judge.change_files("archive/2026-01-01-x")
    assert [f for f, _, _ in files] == ["proposal.md"]
    assert "跳过 design.md" in capsys.readouterr().out


def test_unknown_change_exits(project):
    with pytest.raises(SystemExit):
        judge.change_files("no-such-change")


# ---------- 8. 文案：两种格式与配置 ----------

def test_copy_without_config_exits(project):
    with pytest.raises(SystemExit) as e:
        judge.changed_copy()
    assert "copy.file" in str(e.value)


def test_js_i18n_needs_lang(project):
    _write(project, "openspec/judge.yaml", "copy: {file: index.html, format: js-i18n}\n")
    with pytest.raises(SystemExit) as e:
        judge.copy_config()
    assert "copy.lang" in str(e.value)


def test_json_copy_changed_against_main(project):
    _write(project, "openspec/judge.yaml", "copy: {file: web/zh.json, format: json}\n")
    _write(project, "web/zh.json", json.dumps({"a": {"b": "旧"}, "c": "不变"}, ensure_ascii=False))
    _commit_all(project)
    _write(project, "web/zh.json", json.dumps({"a": {"b": "新"}, "c": "不变", "d": "加"}, ensure_ascii=False))
    assert judge.changed_copy() == {"a.b": "新", "d": "加"}


I18N = """<script>
const I18N = {
  "zh-Hans": { title: "易经", items: ["初", "二"], go: "开始" },
  "zh-Hant": { title: "易經", go: "開始" },
};
</script>"""


def test_js_i18n_copy_reads_one_lang_and_skips_arrays(project):
    _write(project, "openspec/judge.yaml", "copy: {file: index.html, format: js-i18n, lang: zh-Hans}\n")
    _write(project, "index.html", I18N)
    assert judge.changed_copy() == {"title": "易经", "go": "开始"}       # main 上没有这个文件，全部算新增


def test_long_copy_without_copy_rule_goes_review(project, capsys):
    _write(project, "openspec/judgments.yaml", PROJECT_RULE.split("- id: copy-voice")[0])
    _write(project, "openspec/judge.yaml", "copy: {file: web/zh.json, format: json}\n")
    _write(project, "web/zh.json", json.dumps({"a": "服务暂时没有响应，可以稍后重试。"}, ensure_ascii=False))
    results = judge.run_copy(judge.load_rules(), judge.Judge("manual"))
    assert results == ["review"]
    assert "未启用文案打分规则" in capsys.readouterr().out


# ---------- 9. 裁判与 key ----------

def test_provider_defaults_to_manual_without_key(project):
    assert judge.pick_provider() == "manual"


def test_jev_without_key_exits(project, monkeypatch):
    monkeypatch.setenv("JUDGE_PROVIDER", "jev")
    with pytest.raises(SystemExit) as e:
        judge.pick_provider()
    assert "TYPESAFE_API_KEY" in str(e.value)


def test_key_read_from_user_env_file(project, tmp_path, monkeypatch):
    env = tmp_path / "env"
    env.write_text("# key\nTYPESAFE_API_KEY=\"abc\"\n", encoding="utf-8")
    monkeypatch.setattr(judge, "USER_ENV", env)
    assert judge.api_key() == "abc"
    assert judge.pick_provider() == "jev"


def test_env_var_wins_over_user_env_file(project, tmp_path, monkeypatch):
    env = tmp_path / "env"
    env.write_text("TYPESAFE_API_KEY=file\n", encoding="utf-8")
    monkeypatch.setattr(judge, "USER_ENV", env)
    monkeypatch.setenv("TYPESAFE_API_KEY", "var")
    assert judge.api_key() == "var"


def test_project_dotenv_is_ignored(project):
    _write(project, "api/.env", "TYPESAFE_API_KEY=should-not-be-read\n")
    assert judge.api_key() == ""


def test_dry_run_without_key_prints_payload(project, capsys):
    rule = _rules(project)["design-no-yaml"]
    assert judge.Judge(judge.pick_provider(), dry_run=True).ask("正文", [rule]) == {}
    payload = json.loads(capsys.readouterr().out)
    assert payload["model"] == judge.JEV_MODEL and "design-no-yaml" in payload["questions"]


def test_manual_mode_prints_checklist(project, capsys):
    rule = _rules(project)["design-no-yaml"]
    assert judge.Judge("manual").ask("正文", [rule]) == {}
    assert "[ ] design-no-yaml" in capsys.readouterr().out
