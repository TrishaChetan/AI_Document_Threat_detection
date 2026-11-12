from pathlib import Path

from fastapi.testclient import TestClient

from compare_scans import main as compare_main
from schemas.report_schema import ScanInfo, ScanReport, ScanSummary
from schemas.vulnerability_schema import Vulnerability
from services.scan_diff import diff_reports

XML = Path("../reports/zap/xml")  # tests run from backend/


def report(name, *vulns):
    return ScanReport(
        scan_info=ScanInfo(scanner="OWASP ZAP", report_name=name, target="t", generated_at=""),
        summary=ScanSummary(total=len(vulns), high=0, medium=0, low=0, informational=0),
        vulnerabilities=[Vulnerability(title=t, severity=s, description="", affected_url=u, cwe=c, parameter=p)
                         for t, s, u, c, p in vulns],
    )


def test_new_fixed_persisting_and_changed():
    old = report("old.xml",
                 ("SQL Injection", "High", "http://staging:8080/login?x=1", "89", "user"),
                 ("Missing CSP", "Medium", "http://staging:8080/", "693", ""),
                 ("Cookie No HttpOnly", "Low", "http://staging:8080/", "1004", "sid"))
    new = report("new.xml",
                 ("Missing CSP", "Medium", "http://localhost:3000/", "693", ""),      # same finding, other host
                 ("Cookie No HttpOnly", "Medium", "http://localhost:3000/", "1004", "sid"),  # severity up
                 ("XSS (Reflected)", "High", "http://localhost:3000/search", "79", "q"))
    d = diff_reports(old, new)
    s = d["summary"]
    assert (s["new"], s["fixed"], s["persisting"], s["severity_changed"]) == (1, 1, 1, 1)
    assert d["new"][0]["title"] == "XSS (Reflected)"
    assert d["fixed"][0]["title"] == "SQL Injection"
    assert d["severity_changed"][0]["previous_severity"] == "Low"
    assert s["trend"] == "unchanged"   # one High fixed, one High introduced


def test_identical_scans():
    r = report("a", ("X", "Low", "http://h/a", "1", ""))
    s = diff_reports(r, r)["summary"]
    assert (s["new"], s["fixed"], s["persisting"]) == (0, 0, 1)
    assert s["trend"] == "unchanged"


def test_cli_exit_code_gates_on_new_high(tmp_path, capsys):
    assert compare_main([str(XML / "juiceshop_scan_01.xml"), str(XML / "juiceshop_scan_02.xml"),
                         "--json", str(tmp_path / "d.json")]) == 0
    assert (tmp_path / "d.json").exists()
    assert "Trend:" in capsys.readouterr().out


def test_api_compare_endpoint():
    from api.compare_routes import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    c = TestClient(app)
    with open(XML / "dvwa_scan_01.xml", "rb") as a, open(XML / "dvwa_scan_02.xml", "rb") as b:
        r = c.post("/api/v1/compare", files={"baseline": ("a.xml", a), "current": ("b.xml", b)})
    assert r.status_code == 200
    s = r.json()["comparison"]["summary"]
    assert s["new"] == 4 and s["fixed"] == 1
    bad = c.post("/api/v1/compare", files={"baseline": ("a.txt", b"x"), "current": ("b.xml", b"x")})
    assert bad.status_code == 400
