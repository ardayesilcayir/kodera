from fastapi import APIRouter
from app.api.schemas.models import CoverageAnalyzeRequest

router = APIRouter()

@router.post("/analyze")
async def analyze_coverage(request: CoverageAnalyzeRequest):
    """
    Sadece coverage analizi döner.
    """
    return {
        "coverage_ratio": 95.0,
        "continuity": 98.2,
        "revisit_time": 10.5,
        "redundancy": 2,
        "worst_gap": 15.0
    }
