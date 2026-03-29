import os
import sys
from pathlib import Path

from dotenv import load_dotenv

_BACKEND_ROOT = Path(__file__).resolve().parent
load_dotenv(_BACKEND_ROOT / ".env")


def _is_llm_disabled() -> bool:
    v = os.getenv("DISABLE_LLM", "").strip().lower()
    return v in ("1", "true", "yes", "on")


if _is_llm_disabled():
    print("[*] DISABLE_LLM etkin: HuggingFace indirme ve LLM test atışı çalıştırılmıyor.")
    print("    Optimizasyon API'si etkilenmez; sadece bu yardımcı script atlandı.")
    sys.exit(0)

from huggingface_hub import hf_hub_download, login
from llama_cpp import Llama

# -------------------------------------------------------------------------
# AYARLAR VE TOKEN YAPILANDIRMASI
# -------------------------------------------------------------------------
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_DIR = os.getenv("NLP_MODEL_DIR", str(_BACKEND_ROOT.parent / "models"))

REPO_ID = "bartowski/gemma-2-2b-it-GGUF"
FILENAME = "gemma-2-2b-it-Q4_K_M.gguf"


def download_and_setup_model():
    """HuggingFace üzerinden modeli güvenle modeller (models) klasörüne indirir."""
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        print(f"[+] '{MODEL_DIR}' klasörü oluşturuldu.")

    model_path = os.path.join(MODEL_DIR, FILENAME)

    if os.path.exists(model_path):
        print(f"[*] Model zaten mevcut: {model_path}")
        return model_path

    print(f"[!] Model bulunamadı. HuggingFace üzerinden ({FILENAME}) indiriliyor...")
    if HF_TOKEN:
        login(token=HF_TOKEN)
        print("[+] Huggingface kimlik doğrulaması başarılı (.env dosyasından çekildi).")
    else:
        print("[-] UYARI: HF_TOKEN girilmedi. Model açık kaynak değilse indirme başarısız olabilir!")

    try:
        downloaded_path = hf_hub_download(
            repo_id=REPO_ID,
            filename=FILENAME,
            local_dir=MODEL_DIR,
            local_dir_use_symlinks=False,
            token=HF_TOKEN,
        )
        print(f"[+] Model başarıyla indirildi ve sıkıştırıldı: {downloaded_path}")
        return downloaded_path

    except Exception as e:
        print(f"[-] İndirme Hatası: {str(e)}")
        sys.exit(1)


def test_nlp_engine(model_path):
    """
    CPU ve GPU donanım hızlandırmasını kullanarak modeli RAM'e yükleyip test atışı yapar.
    """
    print("\n[+] Llama.cpp Motoru (Gemma Quantized) Isıtılıyor...")

    try:
        llm = Llama(
            model_path=model_path,
            n_ctx=512,
            n_threads=os.cpu_count() // 2,
            n_gpu_layers=-1,
            flash_attn=True,
            verbose=False,
        )

        system_prompt = (
            "You are an aerospace engineer. Summarize the satellite orbit data concisely "
            "in maximum 4 sentences. Make a clear decision."
        )
        user_prompt = (
            "Data: Delta-V cost 0.15 km/s, Target coverage increased by 100%, but transfer "
            "takes 274 hours, violating maximum limits. State if it is recommended or not."
        )

        combined_prompt = f"{system_prompt}\n\nUser Request: {user_prompt}"

        print("[!] Soru (Prompt) Gemma'ya gönderiliyor...\n")

        response = llm.create_chat_completion(
            messages=[{"role": "user", "content": combined_prompt}],
            max_tokens=60,
            temperature=0.1,
        )

        print("================= GEMMA YANITI =================\n")
        print(response["choices"][0]["message"]["content"])
        print("\n===================================================")
        print("[+] Test mükemmel şekilde sonuçlandı. Hafıza (Context) temizleniyor.")

    except Exception as e:
        print(f"[-] Motor Çalıştırma Hatası: {str(e)}")


if __name__ == "__main__":
    path = download_and_setup_model()
    test_nlp_engine(path)
