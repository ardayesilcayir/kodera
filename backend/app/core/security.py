import json
import base64
from cryptography.fernet import Fernet
import os

# Uygulama genelinde kullanılacak statik veya gizli bir anahtar (Demo amaçlı sabit üretiyoruz ancak gerçek senaryoda ENV'den alınmalı)
# Gerçek senaryo: SECRET_KEY = os.getenv("ORBITA_SECRET_KEY", Fernet.generate_key().decode())
SECRET_KEY = b'G1C_T_p7y0U3uS9gWbMjK_dC42C6uO5iF2dJvY5Jk_A=' # Önceden üretilmiş 32 url-safe base64 anahtar

fernet = Fernet(SECRET_KEY)

def encrypt_dict(data: dict) -> str:
    """ Python sözlüğünü (dict) JSON'a çevirip şifreler ve Base64 token döner. """
    json_data = json.dumps(data)
    encrypted_bytes = fernet.encrypt(json_data.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")

def decrypt_dict(encrypted_token: str) -> dict:
    """ Şifreli token'ı çözer ve tekrar Python sözlüğüne (dict) dönüştürür. """
    decrypted_bytes = fernet.decrypt(encrypted_token.encode("utf-8"))
    return json.loads(decrypted_bytes.decode("utf-8"))
