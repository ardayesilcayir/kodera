from fastapi import APIRouter
from app.api.schemas.models import DesignRequest

router = APIRouter()

@router.post("/run")
async def run_design(request: DesignRequest):
    """
    Mission-Based Design akışını çalıştırır
    """
    # Servis çağrısı
    return {
        "recommended_constellation": {
            "orbit_type": "LEO",
            "altitude": 550.0,
            "inclination": 45.0,
            "plane_count": 6,
            "satellite_count": 24,
            "phase_layout": "Walker-Star"
        },
        "metrics": {
            "coverage_ratio": 98.5,
            "continuity": 95.0,
            "revisit_time": 10.5,
            "redundancy": 2,
            "max_gap": 15.0
        },
        "alternatives": [
            {
                "type": "Cost Optimized",
                "satellite_count": 12,
                "coverage": 85.0
            },
            {
                "type": "Balanced",
                "satellite_count": 24,
                "coverage": 98.5
            },
            {
                "type": "Resilient",
                "satellite_count": 48,
                "coverage": 99.9
            }
        ],
        "explanation": {
            "satellite_count_reason": "Seçili bölge üzerinde %98+ kapsama sağlamak için minimum 24 uydu hesaplandı.",
            "inclination_reason": f"Görevin {request.mission.type} tipinde ve enlemlerine göre 45 derece eğim optimum bulundu."
        }
    }
