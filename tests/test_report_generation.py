from reports.report_builder import ReportBuilder
from reports.pdf_generator import PDFGenerator
from schemas.ai_response_schema import AIRecommendation


def sample_vulnerabilities():

    return [

        AIRecommendation(
            title="Content Security Policy (CSP) Header Not Set",
            summary="Content Security Policy header is missing.",
            business_impact="Attackers may execute malicious JavaScript through XSS attacks.",
            technical_analysis="The application does not define a Content-Security-Policy HTTP header.",
            remediation_steps=[
                "Add a Content-Security-Policy header.",
                "Avoid unsafe-inline directives.",
                "Test using Report-Only mode."
            ],
            priority="High"
        ),

        AIRecommendation(
            title="Cookie No HttpOnly Flag",
            summary="Session cookie lacks the HttpOnly flag.",
            business_impact="Cookies can be accessed by JavaScript if XSS exists.",
            technical_analysis="Authentication cookies are created without the HttpOnly attribute.",
            remediation_steps=[
                "Enable HttpOnly.",
                "Review framework configuration.",
                "Retest the application."
            ],
            priority="Medium"
        ),

        AIRecommendation(
            title="Server Leaks Version Information",
            summary="Server header exposes software version.",
            business_impact="Version disclosure assists attackers in fingerprinting the server.",
            technical_analysis="The HTTP Server header reveals Apache version information.",
            remediation_steps=[
                "Disable version disclosure.",
                "Set ServerTokens Prod.",
                "Disable ServerSignature."
            ],
            priority="Low"
        )

    ]


def main():

    vulnerabilities = sample_vulnerabilities()

    builder = ReportBuilder()

    report = builder.build(

        target="http://localhost:8082",

        vulnerabilities=vulnerabilities

    )

    pdf = PDFGenerator()

    filename = pdf.generate(report)

    print()

    print("=" * 50)

    print("Report Generated Successfully")

    print(f"Saved As : {filename}")

    print("=" * 50)


if __name__ == "__main__":
    main()