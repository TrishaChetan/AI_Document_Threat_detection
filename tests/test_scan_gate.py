import json
from datetime import date
from pathlib import Path

import pytest

from parsers import parse_report
from scan_gate import main as gate_main
from schemas.report_schema import ScanInfo, ScanReport, ScanSummary
from schemas.vulnerability_schema import Vulnerability
from services.scan_gate import Policy, evaluate, github_annotations, markdown_summary

XML = Path("../reports/zap/xml")
TODAY = date(2026, 11, 19)


def rep(*vulns):
    vs = [Vulnerability(title=t, severity=s, description="d", affected_url="http://app/" + t[:3], cwe=c)
          for t, s, c in vulns]
    return ScanReport(scan_info=ScanInfo(scanner="OWASP ZAP", report_name="r", target="http://app", generated_at=""),
                      summary=ScanSummary(total=len(vs), high=0, medium=0, low=0, informational=0), vulnerabilities=vs)


SQLI = ("SQL Injection", "High", "89")
CSP = ("CSP Header Not Set", "Medium", "693")
COOKIE = ("Cookie No HttpOnly Flag", "Low", "1004")


def test_fail_on_and_budgets():
    assert not evaluate(rep(SQLI, CSP), Policy(), today=TODAY)["passed"]
    assert evaluate(rep(CSP, COOKIE), Policy(), today=TODAY)["passed"]
    res = evaluate(rep(CSP, COOKIE, ("X-Frame", "Medium", "1021")), Policy(max={"Medium": 1}), today=TODAY)
    assert not res["passed"] and res["violations"][0]["type"] == "budget"
    assert evaluate(rep(SQLI), Policy(fail_on="none"), today=TODAY)["passed"]


def test_ignores_with_expiry_and_cwe():
    p = Policy.from_dict({"fail_on": "low", "ignore": [{"match": "cookie no httponly flag", "until": "2026-12-31"},
                                                        {"match": "cwe:693", "reason": "tracked"}]})
    res = evaluate(rep(CSP, COOKIE), p, today=TODAY)
    assert res["passed"] and len(res["waived"]) == 2
    later = evaluate(rep(CSP, COOKIE), p, today=date(2027, 1, 2))
    assert not later["passed"] and later["expired_ignores"][0]["match"] == "cookie no httponly flag"
    assert any(a.startswith("::warning") for a in github_annotations(later))


def test_baseline_only_counts_new_findings():
    old = rep(SQLI, CSP)
    assert evaluate(rep(SQLI, CSP), Policy(), baseline=old, today=TODAY)["passed"]      # legacy High tolerated
    res = evaluate(rep(SQLI, CSP, ("Remote OS Command Injection", "High", "78")), Policy(), baseline=old, today=TODAY)
    assert not res["passed"] and len(res["violations"]) == 1


def test_bad_policy():
    with pytest.raises(ValueError):
        Policy.from_dict({"fail_on": "urgent"})
    with pytest.raises(ValueError):
        Policy.from_dict({"ignore": [{"match": "x", "until": "soon"}]})


def test_cli_exit_codes_and_github_summary(tmp_path, monkeypatch, capsys):
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    r2, r1 = str(XML / "juiceshop_scan_02.xml"), str(XML / "juiceshop_scan_01.xml")
    assert gate_main([r2]) == 0
    assert gate_main([r2, "--baseline", r1, "--fail-on", "medium", "--github"]) == 1
    out = capsys.readouterr().out
    assert "::error title=Security gate::Medium" in out
    assert summary.read_text().startswith("### Security gate: ⛔ failed")
    policy = tmp_path / "p.json"
    policy.write_text(json.dumps({"fail_on": "informational"}))
    assert gate_main([r2, "--policy", str(policy)]) == 1
    assert gate_main([r2, "--max", "medium=two"]) == 2
    assert gate_main(["missing.xml"]) == 2
    assert Policy.load("../zap-gate.example.json").max == {"Medium": 5, "Low": 20}
    assert "Accepted risks" in markdown_summary(evaluate(rep(COOKIE), Policy.load("../zap-gate.example.json"), today=TODAY))
