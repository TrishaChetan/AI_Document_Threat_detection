import json

from schemas.vulnerability_schema import Vulnerability


class PromptBuilder:

    @staticmethod
    def build(vulnerability: Vulnerability):

        schema = {
            "summary": "",
            "business_impact": "",
            "technical_analysis": "",
            "remediation_steps": [
                "",
                "",
                ""
            ],
            "priority": ""
        }

        return f"""
You are a Senior Penetration Tester and Application Security Consultant.

Analyze the following vulnerability.

Title:
{vulnerability.title or ""}

Severity:
{vulnerability.severity or ""}

Confidence:
{vulnerability.confidence or ""}

Description:
{vulnerability.description or ""}

Affected URL:
{vulnerability.affected_url or ""}

Parameter:
{vulnerability.parameter or ""}

Evidence:
{vulnerability.evidence or ""}

CWE:
{vulnerability.cwe or ""}

WASC:
{vulnerability.wasc or ""}

Return ONLY valid JSON.

Keep every field concise.

Do not exceed 300 words total.

Do not use markdown.

The "priority" field must be one of:
LOW
MEDIUM
HIGH
CRITICAL

Use exactly this JSON schema:

{json.dumps(schema, indent=4)}
"""