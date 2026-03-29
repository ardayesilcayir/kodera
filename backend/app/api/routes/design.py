from fastapi import APIRouter
from typing import Dict, Any

from fastapi.concurrency import run_in_threadpool
# 1. İlk olarak Facade'i yükleriz ki sys.path enjeksiyonları (design_module, maneuver_module) gerçekleşsin
from app.services.orbital_engine.engine_facade import OrbitalEngineFacade
# 2. Sonra Pydantic modelleri ve şemaları yükleriz
from app.api.schemas.models import DecryptRequest, RepositionScenarioRequest, OrbitDesignRequest
from app.core.security import encrypt_dict, decrypt_dict
from app.services.nlp_service import NLPService

router = APIRouter()

@router.post("/generate")
async def generate_constellation(request: OrbitDesignRequest):
    """
    Sıfırdan bir uydu görevi (Constellation) tasarımı yaratır. Pydantic şemasını zorunlu tutar.
    optimization_location algoritmasını CPU-Bound threadpool üzerinde tetikler.
    """
    try:
        # FastAPI Event Loop kilitlenmemesi için senkron matematik motorunu arka planda havuzda çalıştırır
        payload_dict = request.model_dump() if hasattr(request, 'model_dump') else request.dict()
        result = await run_in_threadpool(OrbitalEngineFacade.run_design_optimization, payload_dict)
        
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
async def reposition_satellite(request: RepositionScenarioRequest):
    """
    Mevcut bir uyduyu başka bir yörüngeye kaydırma senaryosunu işletir. Pydantic şemasını zorunlu tutar.
    to_move algoritmasını CPU-Bound threadpool üzerinde tetikler.
    """
    try:
        # FastAPI Event Loop kilitlenmemesi için senkron manevra motorunu arka planda havuzda çalıştırır
        payload_dict = request.model_dump() if hasattr(request, 'model_dump') else request.dict()
        result = await run_in_threadpool(OrbitalEngineFacade.run_reposition_scenario, payload_dict)
        
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
