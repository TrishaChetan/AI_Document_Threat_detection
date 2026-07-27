from pydantic import BaseModel

from schemas.vulnerability_schema import Vulnerability


class ScanInfo(BaseModel):
    """Metadata about the security scan."""

    scanner: str
    report_name: str
    target: str
    generated_at: str


class ScanSummary(BaseModel):
    """Summary of vulnerability counts."""

    total: int
    high: int
    medium: int
    low: int
    informational: int
    unknown: int = 0


class ScanReport(BaseModel):
    """Complete parsed scan report."""

    scan_info: ScanInfo
    summary: ScanSummary
    vulnerabilities: list[Vulnerability]