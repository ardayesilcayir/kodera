from fastapi import APIRouter
from typing import Dict, Any

from app.api.schemas.models import DesignRequest, DecryptRequest
from app.core.security import encrypt_dict, decrypt_dict
from app.services.orbital_engine.engine_facade import OrbitalEngineFacade
from app.services.nlp_service import NLPService

router = APIRouter()

@router.post("/generate")
async def generate_constellation(request: Dict[str, Any]):
    """
    Sıfırdan bir uydu görevi (Constellation) tasarımı yaratır.
    optimization_location algoritmasını tetikler.
    """
    try:
        # Matematik motoruna payload gönder
        result = OrbitalEngineFacade.run_design_optimization(request)
        
        # Fizik motorunun rakamsal verilerini NLP'ye (Gemma) gönderip mühendislik yorumu al
        ai_summary = NLPService.generate_engineering_summary(result, "Constellation Optimization (Walker)")
        
        # NLP Yorumunu veriye ekle
        result["ai_engineering_summary"] = ai_summary
        
        # Sonucu güvenli hale getir
        encrypted_payload = encrypt_dict(result)
        
        return {
            "status": "success",
            "feature": "constellation_design",
            "encrypted_data": encrypted_payload,
            "raw_preview": {
                "total_evaluations": len(result.get("evaluations", [])),
                "ai_summary_preview": ai_summary[:60] + "..."
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/reposition")
async def reposition_satellite(request: Dict[str, Any]):
    """
    Mevcut bir uyduyu başka bir yörüngeye kaydırma senaryosunu işletir.
    to_move algoritmasını tetikler.
    """
    try:
        # Manevra motoruna payload gönder
        result = OrbitalEngineFacade.run_reposition_scenario(request)
        
        # Fizik motorunun rakamsal verilerini NLP'ye (Gemma) gönderip mühendislik yorumu al
        ai_summary = NLPService.generate_engineering_summary(result, "Satellite Reposition (J2 Drift & Delta-V Maneuver)")
        
        # NLP Yorumunu veriye ekle
        result["ai_engineering_summary"] = ai_summary
        
        # Sonucu güvenli hale getir
        encrypted_payload = encrypt_dict(result)
        
        return {
            "status": "success",
            "feature": "satellite_reposition",
            "encrypted_data": encrypted_payload,
            "raw_preview": {
                "best_score": result.get("best_plan", {}).get("final_score"),
                "ai_summary_preview": ai_summary[:60] + "..."
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/decrypt")
async def decrypt_constellation(request: DecryptRequest):
    """
    Şifrelenmiş optimizasyon verisini (token) çözer ve asıl dizilimi geri döndürür.
    """
    try:
        decrypted_data = decrypt_dict(request.encrypted_token)
        return {
            "status": "success",
            "decrypted_data": decrypted_data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Invalid or tampered token: " + str(e)
        }
