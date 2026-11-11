import os
import time
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, File, HTTPException, UploadFile

from ai.recommendation_engine import RecommendationEngine
from parsers import SUPPORTED_EXTENSIONS, get_parser

router = APIRouter()

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

engine = RecommendationEngine()


def analyze_vulnerability(vulnerability):

    ai_analysis = engine.analyze(vulnerability)

    vulnerability_data = vulnerability.model_dump()
    vulnerability_data["ai_analysis"] = ai_analysis.model_dump()

    return vulnerability_data


@router.post("/analyze/xml")
async def analyze_xml(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was uploaded."
        )

    if not file.filename.lower().endswith(SUPPORTED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail="Only OWASP ZAP .xml or .json reports are supported."
        )

    start = time.perf_counter()

    filename = os.path.basename(file.filename)
    temp_path = os.path.join(UPLOAD_DIR, filename)

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:

        parser = get_parser(temp_path)
        report = parser.parse()

        vulnerabilities = report.vulnerabilities

        if vulnerabilities:

            workers = min(4, len(vulnerabilities))

            with ThreadPoolExecutor(max_workers=workers) as executor:

                analyzed_vulnerabilities = list(
                    executor.map(
                        analyze_vulnerability,
                        vulnerabilities
                    )
                )

        else:

            analyzed_vulnerabilities = []

        response = {
            "scan_info": report.scan_info.model_dump(),
            "summary": report.summary.model_dump(),
            "vulnerabilities": analyzed_vulnerabilities
        }

        end = time.perf_counter()

        print(f"\nAnalysis completed in {end - start:.2f} seconds\n")

        return response

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze XML report: {e}"
        )

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)