import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse, Response

from parsers import SUPPORTED_EXTENSIONS, parse_report
from services.findings_export import to_csv, to_sarif
from services.scan_diff import diff_reports

router = APIRouter(tags=["Compare Scans"])


async def _parse_upload(upload: UploadFile, label: str):
    name = upload.filename or ""
    if not name.lower().endswith(SUPPORTED_EXTENSIONS):
        raise HTTPException(400, f"{label}: upload an OWASP ZAP .xml or .json report.")
    suffix = Path(name).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await upload.read())
    try:
        return parse_report(tmp.name)
    except ValueError as e:
        raise HTTPException(400, f"{label}: {e}")
    finally:
        os.unlink(tmp.name)


@router.post("/compare", summary="Compare two scans: new, fixed and still-open findings")
async def compare_scans(
    baseline: UploadFile = File(..., description="Earlier scan report"),
    current: UploadFile = File(..., description="Newer scan report"),
):
    old = await _parse_upload(baseline, "baseline")
    new = await _parse_upload(current, "current")
    return {"success": True, "comparison": diff_reports(old, new)}


@router.post("/export", summary="Convert a ZAP report to SARIF (GitHub code scanning) or CSV")
async def export_findings(
    report: UploadFile = File(..., description="ZAP .xml or .json report"),
    format: str = Query("sarif", pattern="^(sarif|csv)$"),
):
    scan = await _parse_upload(report, "report")
    stem = Path(report.filename or "report").stem
    if format == "csv":
        return Response(to_csv(scan), media_type="text/csv",
                        headers={"Content-Disposition": f'attachment; filename="{stem}-findings.csv"'})
    return JSONResponse(to_sarif(scan), media_type="application/sarif+json",
                        headers={"Content-Disposition": f'attachment; filename="{stem}.sarif"'})
