import os
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile

from parsers import SUPPORTED_EXTENSIONS, get_parser

router = APIRouter(
    prefix="/upload",
    tags=["XML Parser"]
)

TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)


@router.post(
    "/xml",
    summary="Upload and Parse XML Report"
)
async def upload_xml(file: UploadFile = File(...)):

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

    filename = os.path.basename(file.filename)
    file_path = os.path.join(TEMP_DIR, filename)

    try:

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        parser = get_parser(file_path)
        report = parser.parse()

        return report.model_dump()

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to parse XML report."
        )

    finally:

        if os.path.exists(file_path):
            os.remove(file_path)