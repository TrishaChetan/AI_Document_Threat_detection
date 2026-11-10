from types import SimpleNamespace

from reports.executive_summary import ExecutiveSummary
from reports.risk_calculator import RiskCalculator


def vulns(**counts):
    return [SimpleNamespace(priority=p) for p, n in counts.items() for _ in range(n)]


def test_empty_scan():
    r = RiskCalculator.calculate([])
    assert r["overall_score"] == 0
    assert r["rating"] == "None"


def test_score_does_not_saturate():
    # previously both were 100/100
    few = RiskCalculator.calculate(vulns(High=4))["overall_score"]
    many = RiskCalculator.calculate(vulns(High=40))["overall_score"]
    assert few < many <= 100


def test_more_findings_never_lower_the_score():
    prev = 0
    for n in range(1, 30):
        s = RiskCalculator.calculate(vulns(Medium=n))["overall_score"]
        assert s >= prev
        prev = s


def test_single_critical_is_high_risk():
    r = RiskCalculator.calculate(vulns(Critical=1))
    assert r["overall_score"] >= 85
    assert r["rating"] == "Critical"


def test_lows_alone_stay_low():
    r = RiskCalculator.calculate(vulns(Low=3, Informational=10))
    assert r["rating"] == "Low"


def test_summary_advice_matches_findings():
    only_low = ExecutiveSummary.generate(RiskCalculator.calculate(vulns(Low=2)))
    assert "Immediate remediation" not in only_low
    assert "Low severity" in only_low
    severe = ExecutiveSummary.generate(RiskCalculator.calculate(vulns(High=1)))
    assert "Immediate remediation" in severe
