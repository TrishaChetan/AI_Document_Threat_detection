import csv
import io
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from export_findings import main as export_main
from parsers import parse_report
from services.findings_export import _plain, to_csv, to_sarif

XML = Path("../reports/zap/xml")  # tests run from backend/


def test_sarif_structure_on_every_sample():
    for f in sorted(XML.glob("*.xml")):
        rep = parse_report(f)
        s = to_sarif(rep)
        run = s["runs"][0]
        assert s["version"] == "2.1.0" and run["tool"]["driver"]["name"]
        rule_ids = {r["id"] for r in run["tool"]["driver"]["rules"]}
        assert len(run["results"]) == len(rep.vulnerabilities)
        for res in run["results"]:
            assert res["ruleId"] in rule_ids
            assert res["level"] in {"error", "warning", "note", "none"}
            assert res["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
            assert res["message"]["text"]
        for r in run["tool"]["driver"]["rules"]:
            assert 0.0 <= float(r["properties"]["security-severity"]) <= 10.0


def test_high_maps_to_error_with_cwe_tag():
    rep = parse_report(XML / "webgoat_scan_01.xml")
    s = to_sarif(rep)
    highs = [v for v in rep.vulnerabilities if v.severity == "High"]
    if highs:
        assert any(r["level"] == "error" for r in s["runs"][0]["results"])
    assert any(t.startswith("external/cwe/") for r in s["runs"][0]["tool"]["driver"]["rules"]
               for t in r["properties"]["tags"])


def test_csv_sorted_and_cleaned():
    rep = parse_report(XML / "dvwa_scan_01.xml")
    rows = list(csv.DictReader(io.StringIO(to_csv(rep))))
    assert len(rows) == len(rep.vulnerabilities)
    order = {"High": 0, "Medium": 1, "Low": 2, "Informational": 3}
    assert [order[r["severity"]] for r in rows] == sorted(order[r["severity"]] for r in rows)
    assert "<p>" not in "".join(r["description"] for r in rows)
    assert _plain("<p>a &amp; b</p><p>c</p>") == "a & b\nc"


def test_cli_and_api(tmp_path):
    out = tmp_path / "x.sarif"
    assert export_main([str(XML / "dvwa_scan_01.xml"), "-o", str(out)]) == 0
    assert json.loads(out.read_text())["version"] == "2.1.0"
    from api.compare_routes import router
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    c = TestClient(app)
    with open(XML / "dvwa_scan_01.xml", "rb") as fh:
        r = c.post("/api/v1/export?format=csv", files={"report": ("dvwa.xml", fh)})
    assert r.status_code == 200 and r.text.startswith("severity,title")
    with open(XML / "dvwa_scan_01.xml", "rb") as fh:
        r = c.post("/api/v1/export", files={"report": ("dvwa.xml", fh)})
    assert r.headers["content-type"].startswith("application/sarif+json")
    assert c.post("/api/v1/export?format=pdf", files={"report": ("a.xml", b"x")}).status_code == 422
