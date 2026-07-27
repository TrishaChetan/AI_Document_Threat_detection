from fastapi import APIRouter, HTTPException

from database.scan_repository import scan_repository

router = APIRouter(
    prefix="/scans",
    tags=["Scan History"]
)


@router.get(
    "",
    summary="Get all scans"
)
def get_all_scans():

    try:
        return scan_repository.get_all()

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve scan history."
        )


@router.get(
    "/{scan_id}",
    summary="Get scan by ID"
)
def get_scan(scan_id: str):

    try:

        scan = scan_repository.get_by_scan_id(scan_id)

        if not scan:
            raise HTTPException(
                status_code=404,
                detail="Scan not found."
            )

        return scan

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve scan."
        )


@router.delete(
    "/{scan_id}",
    summary="Delete scan"
)
def delete_scan(scan_id: str):

    try:

        deleted = scan_repository.delete(scan_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Scan not found."
            )

        return {
            "success": True,
            "message": "Scan deleted successfully."
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete scan."
        )