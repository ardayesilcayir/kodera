import os
import gc
import json
from llama_cpp import Llama
from dotenv import load_dotenv

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
        # Model ortamda (disk) yoksa erken dön
        if not os.path.exists(MODEL_PATH):
            return "Yapay Zeka (NLP) modeli diskte bulunamadığı için sadece sayısal veriler üretildi."

        # Karmaşık Dictionary verisini küçültme ve düzleştirme (KV Cache şişmesini önlemek için)
        # Çok derin JSON ağaçları modeli boğabilir, o yüzden ilk 800 karakterle sınırlıyoruz
        raw_data_str = json.dumps(data_metrics, ensure_ascii=False)
        compact_data = raw_data_str[:800] + ("..." if len(raw_data_str) > 800 else "")

        # Gemma 2 formatına uygun Sistem Kuralları birleştirme
        system_rules = (
            "You are a professional aerospace engineer. Analyze the following orbital output. "
            "Write exactly 4 sentences explaining the physical feasibility, costs, and coverage impact. "
            "Keep it strictly professional and concise."
        )
        
        user_msg = f"Feature: {feature_type}\nMetrics: {compact_data}\n\nProvide the explanation:"
        combined_prompt = f"{system_rules}\n\nUser Request: {user_msg}"

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
