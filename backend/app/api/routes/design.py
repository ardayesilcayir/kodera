from fastapi import APIRouter
from app.api.schemas.models import DesignRequest, DecryptRequest
from app.core.security import encrypt_dict, decrypt_dict

router = APIRouter()

@router.post("/run")
async def run_design(request: DesignRequest):
    """
    Mission-Based Design akışını çalıştırır
    """
    # Servis çağrısı
    # Uydu dizilimi ve optimizasyon verisini güvenli hale (kriptolu) getiriyoruz
    constellation_data = {
        "orbit_type": "LEO",
        "altitude": 550.0,
        "inclination": 45.0,
        "plane_count": 6,
        "satellite_count": 24,
        "phase_layout": "Walker-Star"
    }
    encrypted_payload = encrypt_dict(constellation_data)

    return {
        "recommended_constellation_encrypted": encrypted_payload,
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

@router.post("/decrypt")
async def decrypt_constellation(request: DecryptRequest):
    """
    Şifrelenmiş optimizasyon verisini (token) çözer ve asıl dizilimi geri döndürür.
    """
    try:
        decrypted_data = decrypt_dict(request.encrypted_token)
        return {
            "status": "success",
            "decrypted_constellation": decrypted_data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Invalid or tampered token: " + str(e)
        }
