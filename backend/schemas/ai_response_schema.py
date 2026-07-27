from typing import Literal

from pydantic import BaseModel


class AIRecommendation(BaseModel):
    """AI-generated recommendation for a vulnerability."""

    summary: str
    business_impact: str
    technical_analysis: str
    remediation_steps: list[str]
    priority: Literal[
        "Critical",
        "High",
        "Medium",
        "Low",
        "Informational",
    ]