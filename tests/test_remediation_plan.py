import csv
import io
import json
from datetime import date
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from parsers import parse_report
from remediation_plan import main as plan_main
from schemas.report_schema import ScanInfo, ScanReport, ScanSummary
from schemas.vulnerability_schema import Vulnerability
from services.remediation_plan import build_plan, parse_sla, scan_date, to_csv, to_markdown

XML = Path("../reports/zap/xml")  # tests run from backend/
TODAY = date(2026, 11, 17)


def report(*vulns, when="Sun, 26 Jul 2026 12:55:12"):
    vs = [Vulnerability(title=t, severity=s, description="d", affected_url=u, cwe=c, solution="<p>Fix it.</p>")
          for t, s, u, c in vulns]
    return ScanReport(scan_info=ScanInfo(scanner="OWASP ZAP", report_name="r", target="http://app", generated_at=when),
                      summary=ScanSummary(total=len(vs), high=0, medium=0, low=0, informational=0),
                      vulnerabilities=vs)


def test_findings_with_one_fix_become_one_ticket():
    rep = report(("Content Security Policy (CSP) Header Not Set", "Medium", "http://app/a", "693"),
                 ("Missing Anti-clickjacking Header", "Medium", "http://app/b", "1021"),
                 ("X-Content-Type-Options Header Missing", "Low", "http://app/a", "693"),
                 ("Cookie No HttpOnly Flag", "Low", "http://app/login", "1004"),
                 ("Cookie without SameSite Attribute", "Low", "http://app/login", "1275"),
                 ("SQL Injection", "High", "http://app/search", "89"),
                 ("Authentication Request Identified", "Informational", "http://app/login", "-1"))
    plan = build_plan(rep, today=TODAY)
    titles = [t["title"] for t in plan["tickets"]]
    assert titles[0].startswith("Fix injection")                       # High first
    headers = next(t for t in plan["tickets"] if t["title"].startswith("Add missing HTTP security headers"))
    assert headers["severity"] == "Medium" and len(headers["findings"]) == 3
    assert headers["urls"] == ["http://app/a", "http://app/b"] and headers["cwes"] == ["693", "1021"]
    assert sum(t["title"].startswith("Harden session cookie") for t in plan["tickets"]) == 1
    assert len(plan["tickets"]) == 3                                   # informational skipped
    assert [t["id"] for t in plan["tickets"]] == ["FIX-01", "FIX-02", "FIX-03"]
    assert len(build_plan(rep, today=TODAY, include_info=True)["tickets"]) == 4


def test_due_dates_and_overdue():
    rep = report(("SQL Injection", "High", "http://app/s", "89"), ("Directory Browsing", "Low", "http://app/d", "548"))
    plan = build_plan(rep, today=TODAY)
    high, low = plan["tickets"]
    assert plan["scan_date"] == "2026-07-26"
    assert high["due"] == "2026-08-25" and high["overdue"] and high["days_left"] == -84
    assert low["due"] == "2027-01-22" and not low["overdue"]
    assert low["title"] == "Directory Browsing" and low["how_to_fix"] == "Fix it."   # unthemed: own ticket, plain text
    fast = build_plan(rep, today=date(2026, 7, 30), sla=parse_sla("high=3"))
    assert fast["tickets"][0]["overdue"] and fast["overdue"] == 1


def test_parse_sla_and_scan_date():
    assert parse_sla("high=14, medium=60,info=400")["Informational"] == 400
    with pytest.raises(ValueError):
        parse_sla("urgent=1")
    assert scan_date(report(when="2026-03-04T10:00:00Z")) == date(2026, 3, 4)


def test_every_sample_report_and_formats():
    for f in sorted(XML.glob("*.xml")):
        plan = build_plan(parse_report(f), today=TODAY)
        assert plan["tickets"], f
        assert plan["findings_in"] >= len(plan["tickets"])
        md = to_markdown(plan)
        assert md.startswith("# Remediation plan") and "FIX-01" in md
        rows = list(csv.DictReader(io.StringIO(to_csv(plan))))
        assert len(rows) == len(plan["tickets"]) and rows[0]["id"] == "FIX-01"


def test_cli_and_api(tmp_path, capsys):
    out = tmp_path / "plan.json"
    assert plan_main([str(XML / "webgoat_scan_01.xml"), "--format", "json", "--today", "2026-11-17", "-o", str(out)]) == 0
    assert json.loads(out.read_text())["tickets"][0]["id"] == "FIX-01"

    from api.compare_routes import router
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    c = TestClient(app)
    data = (XML / "dvwa_scan_01.xml").read_bytes()
    r = c.post("/api/v1/remediation-plan", files={"report": ("dvwa.xml", data, "application/xml")})
    assert r.status_code == 200 and r.json()["plan"]["tickets"]
    r = c.post("/api/v1/remediation-plan?format=md", files={"report": ("dvwa.xml", data, "application/xml")})
    assert r.text.startswith("# Remediation plan") and "dvwa-remediation.md" in r.headers["content-disposition"]
    r = c.post("/api/v1/remediation-plan?sla=urgent=1", files={"report": ("dvwa.xml", data, "application/xml")})
    assert r.status_code == 400
