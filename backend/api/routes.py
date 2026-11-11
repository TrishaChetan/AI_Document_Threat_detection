from datetime import datetime
from pathlib import Path

from parsers import SUPPORTED_EXTENSIONS
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from database.scan_repository import scan_repository
from services.scan_service import scan_service
import traceback

router = APIRouter(tags=["Guardex API"])

REPORTS_DIR = Path(__file__).resolve().parent.parent / "generated_reports"


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Guardex AI API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/scan")
async def start_scan(file: UploadFile = File(...)):

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

    try:

        file_bytes = await file.read()

        saved_file = scan_service.save_uploaded_file(
            file_bytes=file_bytes,
            filename=file.filename
        )

        result = scan_service.process_scan(saved_file)

        return result

    except HTTPException:
        raise

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/history")
async def get_history():
    return {
        "success": True,
        "history": scan_repository.get_all()
    }


@router.get("/scan/{scan_id}")
async def get_scan(scan_id: str):

    scan = scan_repository.get_by_scan_id(scan_id)

    if scan is None:
        raise HTTPException(
            status_code=404,
            detail="Scan not found."
        )

    return {
        "success": True,
        "scan": scan
    }


@router.get("/report/{filename}")
async def download_report(filename: str):

    file_path = REPORTS_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Report not found."
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename
    )


@router.post("/report")
async def generate_report():
    return {
        "success": True,
        "message": "Report endpoint is ready. PDF generation integration coming next."
    }


@router.get("/statistics")
async def get_statistics():

    history = scan_repository.get_all()

    total_scans = len(history)

    reports_generated = sum(
        1
        for scan in history
        if scan.get("pdf_report")
    )

    critical_vulnerabilities = sum(
        scan.get("summary", {}).get("critical", 0)
        for scan in history
    )

    high_vulnerabilities = sum(
        scan.get("summary", {}).get("high", 0)
        for scan in history
    )

    medium_vulnerabilities = sum(
        scan.get("summary", {}).get("medium", 0)
        for scan in history
    )

    low_vulnerabilities = sum(
        scan.get("summary", {}).get("low", 0)
        for scan in history
    )

    return {
        "success": True,
        "statistics": {
            "total_scans": total_scans,
            "reports_generated": reports_generated,
            "knowledge_base_entries": 252,
            "critical_vulnerabilities": critical_vulnerabilities,
            "severity_distribution": {
                "critical": critical_vulnerabilities,
                "high": high_vulnerabilities,
                "medium": medium_vulnerabilities,
                "low": low_vulnerabilities,
            },
        },
    }


@router.get("/info")
async def api_info():
    return {
        "application": "Guardex AI",
        "description": "AI Powered Web Vulnerability Assessment Platform",
        "version": "1.0.0",
        "author": "Guardex Team"
    }