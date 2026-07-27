from typing import Any

from pydantic import BaseModel


class ScanDocument(BaseModel):
    """Represents a stored scan document."""

    scan_id: str
    target: str
    uploaded_at: str
    risk_score: int
    status: str
    pdf_report: str
    summary: dict[str, Any]