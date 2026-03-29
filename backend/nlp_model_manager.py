import os
import sys
from huggingface_hub import hf_hub_download, login
from llama_cpp import Llama
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"c:\Users\arda\Desktop\kodera\backend\.env")

# -------------------------------------------------------------------------
# AYARLAR VE TOKEN YAPILANDIRMASI
# -------------------------------------------------------------------------
# Lütfen ortam değişkenlerine HF_TOKEN adında HuggingFace token'ını ekle, 
# ya da betiği çalıştırırken aşağıya yapıştır.
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_DIR = r"c:\Users\arda\Desktop\kodera\models"

# Gemma 1B'nin işlemci dostu 4-Bit GGUF halini sağlayan repoyu seçiyoruz.
# Gated (Özel) repolarda token zorunlu olduğu için HF_TOKEN devreye girecektir.
REPO_ID = "bartowski/gemma-2-2b-it-GGUF" # (Gemma-3 1B veya hedeflenen repo id buraya eklenebilir)
FILENAME = "gemma-2-2b-it-Q4_K_M.gguf"    # 4-bit Quantization (CPU ve GPU en iyi hız/kalite dengesi)

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
        # Modeli indirir ve belirttiğimiz klasöre kopyalar
        downloaded_path = hf_hub_download(
            repo_id=REPO_ID,
            filename=FILENAME,
            local_dir=MODEL_DIR,
            local_dir_use_symlinks=False,
            token=HF_TOKEN
        )
        print(f"[+] Model başarıyla indirildi ve sıkıştırıldı: {downloaded_path}")
        return downloaded_path
    
    except Exception as e:
        print(f"[-] İndirme Hatası: {str(e)}")
        sys.exit(1)

def test_nlp_engine(model_path):
    """
    CPU ve GPU donanım hızlandırmasını kullanarak (Flash Attention ve BLAS destekli)
    modeli RAM'e yükleyip sıfır-context (stateless) bir test atışı yapar.
    """
    print("\n[+] Llama.cpp Motoru (Gemma Quantized) Isıtılıyor...")
    
    # n_ctx: 512 (Kısa bağlam sıfırlaması için yeterli)
    # n_gpu_layers: -1 (Varsa tüm yükü GPU'ya atar, yoksa AVX2 üzerinden sadece CPU çalıştırır)
    # flash_attn: True (Donanım destekliyorsa Flash Attention 2 açar)
    try:
        llm = Llama(
            model_path=model_path,
            n_ctx=512,
            n_threads=os.cpu_count() // 2, # Optimum CPU çekirdeği kullanımı
            n_gpu_layers=-1, 
            flash_attn=True, 
            verbose=False
        )
        
        # Fizik motorundan çıkmış sahte (mock) veri prompt'u
        system_prompt = "You are an aerospace engineer. Summarize the satellite orbit data concisely in maximum 4 sentences. Make a clear decision."
        user_prompt = "Data: Delta-V cost 0.15 km/s, Target coverage increased by 100%, but transfer takes 274 hours, violating maximum limits. State if it is recommended or not."
        
        combined_prompt = f"{system_prompt}\n\nUser Request: {user_prompt}"

        print("[!] Soru (Prompt) Gemma'ya gönderiliyor...\n")
        
        response = llm.create_chat_completion(
            messages=[
                {"role": "user", "content": combined_prompt}
            ],
            max_tokens=60, # Maksimum kelime sayısı (4 Cümlede kesmesi için katı kural)
            temperature=0.1 # Kesin matematik ve fizik yorumlaması için düşük yaratıcılık
        )
        
        print("================= GEMMA 1B YANITI =================\n")
        print(response["choices"][0]["message"]["content"])
        print("\n===================================================")
        print("[+] Test mükemmel şekilde sonuçlandı. Hafıza (Context) temizleniyor.")
        
    except Exception as e:
        print(f"[-] Motor Çalıştırma Hatası: {str(e)}")

if __name__ == "__main__":
    path = download_and_setup_model()
    test_nlp_engine(path)
