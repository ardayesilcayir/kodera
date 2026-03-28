import os
import sys
import json
from typing import Dict, Any

# =========================================================================
# SYSTEM PATH INJECTION (MİMARİYİ BOZMAMAK İÇİN)
# İki takım arkadaşının yazdığı kodlar birbirine ve dışa bağımlı relative 
# importlar kullanıyor olabilir. Dosyaların kendi importlarını bozmadan 
# çalışması için klasörleri sys.path'e top-level modül olarak ekliyoruz.
# =========================================================================
ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
DESIGN_DIR = os.path.join(ENGINE_DIR, 'design_module')
MANEUVER_DIR = os.path.join(ENGINE_DIR, 'maneuver_module')

if DESIGN_DIR not in sys.path:
    sys.path.insert(0, DESIGN_DIR)
if MANEUVER_DIR not in sys.path:
    sys.path.insert(0, MANEUVER_DIR)

# --- Feature 1: Design Module Imports ---
try:
    from optimizer_service import optimize_regional_coverage
    from request_models import OrbitDesignRequest
    from candidate_models import CandidateGenerationInput
    from optimizer_models import DesignerParams
except ImportError as e:
    print(f"Design Module yüklenemedi: {e}")

# --- Feature 2: Maneuver Module Imports ---
try:
    from reposition_optimizer import optimize_reposition
    from satellite_models import Satellite, MissionConstraints
    from simulation_state import SimulationState
    from target_region import TargetRegion
except ImportError as e:
    print(f"Maneuver Module yüklenemedi: {e}")


class OrbitalEngineFacade:
    """
    Ana Kumanda (Facade): Tüm karmaşık fizik hesaplamalarını dışarıya (FastAPI uç noktalarına)
    kapsülleyerek sunan birleşik servis sınıfıdır. Yüklenen modüllere asla dokunmaz.
    """

    @classmethod
    def run_design_optimization(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sıfırdan bir uzay görevi (Constellation) tasarımı başlatır.
        Gerçekleşecek işlemler: Walker Dizilimi, Hohmann Kapsama Analizi.
        """
        try:
            # Pydantic modellerine parse işlemi
            request = OrbitDesignRequest(**payload)
            cand_input = CandidateGenerationInput()
            params = DesignerParams()
            
            # Motor çalışıyor
            result = optimize_regional_coverage(request, cand_input, params)
            
            # Sonucu JSON serileştirilebilir bir dict'e çevirip dönüyoruz
            return result.model_dump() if hasattr(result, 'model_dump') else result.dict()
        
        except Exception as e:
            return {"error": "Tasarım motorunda hata", "details": str(e)}

    @classmethod
    def run_reposition_scenario(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Var olan uyduyu başka bir hedefe kaydırma operasyonunu başlatır.
        Gerçekleşecek işlemler: Delta-V hesabı, Risk analizi, J2 sürüklenmesi.
        """
        try:
            # Pydantic JSON to Models
            sat = Satellite(**payload.get("satellite", {}))
            region = TargetRegion(**payload.get("target_region", {}))
            constraints = MissionConstraints(**payload.get("constraints", {}))
            sim = SimulationState(**payload.get("sim_state", {}))
            
            result = optimize_reposition(
                satellite=sat,
                target_region=region,
                mission_type=payload.get("mission_type", "communication"),
                sim_state=sim,
                constraints=constraints
            )
            
            return result.model_dump() if hasattr(result, 'model_dump') else result.dict()
            
        except Exception as e:
            return {"error": "Manevra motorunda hata", "details": str(e)}
