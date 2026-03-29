from fastapi import APIRouter, HTTPException, Depends
from app.api.schemas.auth import UserSignup, UserLogin, TokenResponse
from app.db.supabase import supabase
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/signup")
async def signup(data: UserSignup):
    """
    Supabase auth.users tablosu üzerinden yeni üye kaydı açar.
    Başarılı olursa anında oturum açıp JWT token döner.
    """
    try:
        res = supabase.auth.sign_up({
            "email": data.email, 
            "password": data.password,
            "options": {
                "data": {
                    "full_name": data.full_name
                }
            }
        })
        
        if res.session:
            return TokenResponse(
                access_token=res.session.access_token,
                refresh_token=res.session.refresh_token
            )
        else:
            return {"status": "success", "message": "Kayıt başarılı, lütfen e-posta adresinize gelen doğrulama linkine tıklayın. (Eğer Supabase'den Confirm Email kapalı ise bu durumu göz ardı edebilirsiniz)"}
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    """
    E-posta ve şifresi doğrulanan üyeler için geçerli bir JWT (Erişim Token'i) döner.
    Bu token ileride korumalı yörünge rotalarında Authorization: Bearer <TOKEN> olarak kullanılacaktır.
    """
    try:
        res = supabase.auth.sign_in_with_password({
            "email": data.email, 
            "password": data.password
        })
        return TokenResponse(
            access_token=res.session.access_token,
            refresh_token=res.session.refresh_token
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail="E-posta veya şifre hatalı ya da hesap onaylanmamış. Detay: " + str(e))


@router.get("/me")
async def get_me_test_route(user = Depends(get_current_user)):
    """
    [TEST ROTA]
    Sadece sistemde oturum açmış yetkili kullanıcılara (Bearer Session sahiplerine) profil özetlerini döner.
    Kullanıcı token'ı olmadan sorgulandığında otomatik 401 Unauthorized uyarısı verir.
    """
    return {
        "status": "success",
        "message": "Token doğrulandı! Bu gizli/korumalı bilgi sadece yetkili oturumlara gösterilir.",
        "user_id": user.id,
        "email": user.email,
        "metadata": user.user_metadata
    }
