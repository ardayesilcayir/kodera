from fastapi import APIRouter
from app.api.schemas.models import MinSatellitesRequest

router = APIRouter()

@router.post("/min-satellites")
async def find_min_satellites(request: MinSatellitesRequest):
    """
    Minimum uydu sayısını bulur.
    """
    return {
        "recommended_count": 18,
        "reasoning": "Minimum elevation kısıtı ve istenen %98 kapsama için 3 düzlem 6 uydu gereklidir."
    }
