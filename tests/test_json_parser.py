import json
from pathlib import Path

import pytest
from lxml import etree

from parsers import get_parser, parse_report
from parsers.json_parser import JSONParser
from parsers.xml_parser import XMLParser

XML_DIR = Path("../reports/zap/xml")  # tests run from backend/ (see conftest.py)


def xml_to_zap_json(xml_path: Path) -> dict:
    """Build the equivalent ZAP 'Traditional JSON' report from an XML one."""
    root = etree.parse(str(xml_path)).getroot()
    sites = []
    for site in root.findall("site"):
        alerts = []
        for a in site.findall("alerts/alertitem"):
            alerts.append({
                "alert": a.findtext("alert", ""), "name": a.findtext("name", ""),
                "riskcode": a.findtext("riskcode", "0"), "confidence": a.findtext("confidence", ""),
                "riskdesc": a.findtext("riskdesc", ""), "desc": a.findtext("desc", ""),
                "solution": a.findtext("solution", ""), "reference": a.findtext("reference", ""),
                "cweid": a.findtext("cweid", ""), "wascid": a.findtext("wascid", ""),
                "instances": [{"uri": i.findtext("uri", ""), "param": i.findtext("param", ""),
                               "evidence": i.findtext("evidence", "")}
                              for i in a.findall("instances/instance")],
            })
        sites.append({"@name": site.get("name", ""), "alerts": alerts})
    return {"@version": "2.15.0", "@generated": root.get("generated", ""), "site": sites}


@pytest.mark.parametrize("xml_path", sorted(XML_DIR.glob("*.xml")), ids=lambda p: p.name)
def test_json_matches_xml(tmp_path, xml_path):
    json_path = tmp_path / (xml_path.stem + ".json")
    json_path.write_text(json.dumps(xml_to_zap_json(xml_path)))
    from_xml = XMLParser(xml_path).parse()
    from_json = JSONParser(json_path).parse()
    assert from_json.summary == from_xml.summary
    assert [v.title for v in from_json.vulnerabilities] == [v.title for v in from_xml.vulnerabilities]
    assert [v.severity for v in from_json.vulnerabilities] == [v.severity for v in from_xml.vulnerabilities]
    assert from_json.vulnerabilities[0].affected_url == from_xml.vulnerabilities[0].affected_url


def test_multiple_sites_are_all_included(tmp_path):
    report = {"@generated": "now", "site": [
        {"@name": "https://a.example", "alerts": [{"alert": "XSS", "riskcode": "3", "instances": [{"uri": "https://a.example/x"}]}]},
        {"@name": "https://b.example", "alerts": [{"alert": "CSP missing", "riskcode": "2"}]},
    ]}
    p = tmp_path / "multi.json"
    p.write_text(json.dumps(report))
    r = parse_report(p)
    assert r.summary.total == 2 and r.summary.high == 1 and r.summary.medium == 1
    assert r.scan_info.target == "https://a.example, https://b.example"


def test_bad_input(tmp_path):
    (tmp_path / "x.json").write_text("{not json")
    with pytest.raises(ValueError, match="Invalid JSON"):
        parse_report(tmp_path / "x.json")
    (tmp_path / "y.json").write_text('{"foo": 1}')
    with pytest.raises(ValueError, match="Missing 'site'"):
        parse_report(tmp_path / "y.json")
    with pytest.raises(ValueError, match="Unsupported"):
        get_parser("report.pdf")
