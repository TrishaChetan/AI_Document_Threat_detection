import os
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile

from parsers.xml_parser import XMLParser

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

    if not file.filename.lower().endswith(".xml"):
        raise HTTPException(
            status_code=400,
            detail="Only XML files are allowed."
        )

    filename = os.path.basename(file.filename)
    file_path = os.path.join(TEMP_DIR, filename)

    try:

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        parser = XMLParser(file_path)
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