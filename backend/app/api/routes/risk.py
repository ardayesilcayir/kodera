from fastapi import APIRouter
from app.api.schemas.models import FailureRequest

router = APIRouter()

@router.post("/failure")
async def failure_simulation(request: FailureRequest):
    """
    Failure simulation çalıştırır.
    """
    return {
        "constellation_id": request.constellation_id,
        "failed_sat": request.failed_satellite_id,
        "impact": "Yüzde 5 kapsama düşüşü",
        "weak_zones": ["Bölge kuzeybatısı"]
    }
