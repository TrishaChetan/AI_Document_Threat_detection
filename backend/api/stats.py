from fastapi import APIRouter, HTTPException

from ai.knowledge_base import KnowledgeBase
from ai.statistics import KnowledgeBaseStatistics

router = APIRouter(
    prefix="/stats",
    tags=["Statistics"]
)

kb = KnowledgeBase()
stats = KnowledgeBaseStatistics(kb)


@router.get(
    "/",
    summary="Get Knowledge Base Statistics"
)
def get_statistics():

    try:
        kb.reload()
        return stats.summary()

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve knowledge base statistics."
        )