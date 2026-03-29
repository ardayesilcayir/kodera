import os
import gc
import json
from dotenv import load_dotenv

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    Llama = None

# Env yüklenmesi (Huggingface vb.)
load_dotenv(dotenv_path=r"c:\Users\arda\Desktop\kodera\backend\.env")
MODEL_PATH = r"c:\Users\arda\Desktop\kodera\models\gemma-2-2b-it-Q4_K_M.gguf"

class NLPService:
    """
    Sistemin ürettiği saf matematiksel (Orbit, Walker vb.) çıktıları
    Uzay Mühendisi diliyle 4-5 cümlede özetleyen Zeki Raporlayıcı.
    %100 Stateless (Durumsuz) çalışır. İşlem bitince RAM'den kendini patlatır.
    """

    @staticmethod
    def generate_engineering_summary(data_metrics: dict, feature_type: str) -> str:
        """
        JSON tabanlı sayısal fizik verisini, Gemma 2B LLM motoruna sokar
        ve doğal dilde mühendislik yorumuna çevirir.
        """
        if not LLAMA_AVAILABLE:
            return "Yapay Zeka (NLP) kütüphanesi (llama-cpp-python) sistemde kurulu değil, sadece matematiksel veriler üretildi:\n\n" + compact_data

        # Model ortamda (disk) yoksa erken dön
        if not os.path.exists(MODEL_PATH):
            return "Yapay Zeka (NLP) modeli diskte bulunamadığı için sadece sayısal veriler üretildi:\n\n" + compact_data

        # Modeli boğmamak (KV Cache oom) ve halüsinasyonu engellemek için, sadece önemli metrikleri "cımbızlıyoruz"
        summary_dict = {}
        if "Walker" in feature_type:
            # Constellation (Walker) modu için kritik KPI'ları ayıkla
            top_plans = data_metrics.get("evaluations", [])[:3]
            summary_dict = {
                "total_candidate_count": len(data_metrics.get("evaluations", [])),
                "best_recommended_candidates": [
                    {
                        "orbit_type": p.get("orbit", {}).get("type"),
                        "satellites": p.get("orbit", {}).get("total_satellites"),
                        "planes": p.get("orbit", {}).get("planes"),
                        "coverage_score": p.get("coverage", {}).get("score", 0),
                        "cost": p.get("cost", 0)
                    } for p in top_plans if isinstance(p, dict)
                ][:1]
            }
        elif "Reposition" in feature_type:
            # Manevra modu için kritik KPI'ları ayıkla
            best_plan = data_metrics.get("best_plan", {})
            summary_dict = {
                "top_score": best_plan.get("final_score"),
                "status": best_plan.get("operational_status"),
                "transfer_metrics": best_plan.get("transfer_summary", {}),
                "risk_breakdown": best_plan.get("risk_analysis", {}).get("risk_factors", [])
            }
        else:
            summary_dict = {"raw_preview": str(data_metrics)[:200]}

        compact_data = json.dumps(summary_dict, ensure_ascii=False)

        # Gemma 2 formatına uygun Sistem Kuralları birleştirme
        system_rules = (
            "Sen uzman bir uzay mühendisisin. Lütfen yanıtını KESİNLİKLE TÜRKÇE ver. "
            "Aşağıdaki yörünge (orbital) çıktılarını incele. Sonucu, donanım maliyetleri, kapsama alanı ve "
            "fiziksel yapılabilirlik açısından değerlendirip en fazla 3-4 cümlelik sade, anlaşılır ve özet bir Türkçe rapor yaz."
        )
        
        user_msg = f"Simülasyon Türü: {feature_type}\nSonuç Metrikleri: {compact_data}\n\nLütfen kapsamlı ve anlaşılır Türkçe mühendislik özetini yazın:"
        combined_prompt = f"{system_rules}\n\n[Kullanıcı İstemi]: {user_msg}"

        llm = None
        analysis_text = ""
        
        try:
            # 1) Modeli sıfırdan belleğe yükle (Sıfır Geçmiş - Stateless)
            # n_ctx=512 ile RAM kullanımı katı bir şekilde kısıtlanır. CPU üzerinde koşar.
            llm = Llama(
                model_path=MODEL_PATH,
                n_ctx=512,
                n_gpu_layers=0,  # GPU kullanılmayacak
                verbose=False    # Terminal gürültüsünü kesme
            )

            # 2) Çıkarım (Inference)
            response = llm.create_chat_completion(
                messages=[{"role": "user", "content": combined_prompt}],
                max_tokens=100,
                temperature=0.1  # Matematiksel netlik için düşük yaratıcılık
            )

            analysis_text = response["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            analysis_text = f"NLP Çıkarım (Inference) Hatası: {str(e)}"
            
        finally:
            # 3) KATI RAM YÖNETİMİ (Garbage Collection)
            # İşlemci ve Bellekten modeli acımasızca söküp at.
            # Bir dahaki API isteğinde 'sanki sıfırdan yükleniyormuş' gibi tekrar yüklenecek.
            if llm is not None:
                del llm
            gc.collect()

        return analysis_text
