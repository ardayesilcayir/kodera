import gc
import json
import os
from pathlib import Path

from dotenv import load_dotenv

try:
    from llama_cpp import Llama

    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    Llama = None

# backend/ dizinine göre .env ve varsayılan model yolu (sabit Windows yolu yok)
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _BACKEND_ROOT / ".env"
load_dotenv(_ENV_FILE)

_DEFAULT_MODEL_REL = Path("models") / "gemma-2-2b-it-Q4_K_M.gguf"
MODEL_PATH = os.getenv(
    "GEMMA_MODEL_PATH",
    str((_BACKEND_ROOT.parent / _DEFAULT_MODEL_REL).resolve()),
)


def _is_llm_disabled() -> bool:
    """DISABLE_LLM=1|true|yes|on → bu makinede LLM çıkarımı yapılmaz; optimizasyon aynen çalışır."""
    v = os.getenv("DISABLE_LLM", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _build_summary_dict(data_metrics: dict, feature_type: str) -> dict:
    summary_dict: dict = {}
    if "Walker" in feature_type:
        top_plans = data_metrics.get("evaluations", [])[:3]
        summary_dict = {
            "total_candidate_count": len(data_metrics.get("evaluations", [])),
            "best_recommended_candidates": [
                {
                    "orbit_type": p.get("orbit", {}).get("type"),
                    "satellites": p.get("orbit", {}).get("total_satellites"),
                    "planes": p.get("orbit", {}).get("planes"),
                    "coverage_score": p.get("coverage", {}).get("score", 0),
                    "cost": p.get("cost", 0),
                }
                for p in top_plans
                if isinstance(p, dict)
            ][:1],
        }
    elif "Reposition" in feature_type:
        best_plan = data_metrics.get("best_plan", {})
        summary_dict = {
            "top_score": best_plan.get("final_score"),
            "status": best_plan.get("operational_status"),
            "transfer_metrics": best_plan.get("transfer_summary", {}),
            "risk_breakdown": best_plan.get("risk_analysis", {}).get("risk_factors", []),
        }
    else:
        summary_dict = {"raw_preview": str(data_metrics)[:200]}
    return summary_dict


class NLPService:
    """
    Sistemin ürettiği saf matematiksel (Orbit, Walker vb.) çıktıları
    Uzay Mühendisi diliyle özetleyen isteğe bağlı LLM katmanı.
    DISABLE_LLM ile tamamen devre dışı bırakılabilir.
    """

    @staticmethod
    def generate_engineering_summary(data_metrics: dict, feature_type: str) -> str:
        """
        JSON tabanlı sayısal fizik verisini, istenirse Gemma GGUF ile doğal dil özetine çevirir.
        """
        summary_dict = _build_summary_dict(data_metrics, feature_type)
        compact_data = json.dumps(summary_dict, ensure_ascii=False)

        if _is_llm_disabled():
            return (
                "[LLM devre dışı: DISABLE_LLM] Mühendislik özeti üretilmedi; "
                "sadece optimizasyon / sayısal sonuçlar kullanıldı.\n\n"
                f"Özetlenecek önizleme: {compact_data[:500]}"
                + ("…" if len(compact_data) > 500 else "")
            )

        if not LLAMA_AVAILABLE:
            return (
                "Yapay Zeka (NLP) kütüphanesi (llama-cpp-python) sistemde kurulu değil, "
                "sadece matematiksel veriler üretildi:\n\n" + compact_data
            )

        if not os.path.exists(MODEL_PATH):
            return (
                "Yapay Zeka (NLP) modeli diskte bulunamadığı için sadece sayısal veriler üretildi:\n\n"
                + compact_data
            )

        system_rules = (
            "Sen uzman bir uzay mühendisisin. Lütfen yanıtını KESİNLİKLE TÜRKÇE ver. "
            "Aşağıdaki yörünge (orbital) çıktılarını incele. Sonucu, donanım maliyetleri, kapsama alanı ve "
            "fiziksel yapılabilirlik açısından değerlendirip en fazla 3-4 cümlelik sade, anlaşılır ve özet bir Türkçe rapor yaz."
        )

        user_msg = (
            f"Simülasyon Türü: {feature_type}\nSonuç Metrikleri: {compact_data}\n\n"
            "Lütfen kapsamlı ve anlaşılır Türkçe mühendislik özetini yazın:"
        )
        combined_prompt = f"{system_rules}\n\n[Kullanıcı İstemi]: {user_msg}"

        llm = None
        analysis_text = ""

        try:
            llm = Llama(
                model_path=MODEL_PATH,
                n_ctx=512,
                n_gpu_layers=0,
                verbose=False,
            )

            response = llm.create_chat_completion(
                messages=[{"role": "user", "content": combined_prompt}],
                max_tokens=100,
                temperature=0.1,
            )

            analysis_text = response["choices"][0]["message"]["content"].strip()

        except Exception as e:
            analysis_text = f"NLP Çıkarım (Inference) Hatası: {str(e)}"

        finally:
            if llm is not None:
                del llm
            gc.collect()

        return analysis_text
