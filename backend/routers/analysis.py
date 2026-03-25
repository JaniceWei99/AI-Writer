from fastapi import APIRouter
from pydantic import BaseModel
from services.text_analysis import analyze_text

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


class AnalyzeRequest(BaseModel):
    content: str


@router.post("/quality")
async def quality_analysis(req: AnalyzeRequest):
    """Analyze text quality using pure algorithms (no AI)."""
    return analyze_text(req.content)
