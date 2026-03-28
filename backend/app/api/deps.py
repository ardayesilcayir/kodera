from fastapi import Header, HTTPException, Depends
from app.db.supabase import supabase

def get_current_user(authorization: str = Header(None)):
    """
    HTTP isteğinin Header'ı içerisinden 'Authorization: Bearer <TOKEN>' bekler.
    Token'i Supabase veritabanında doğrular ve geçerliyse kullanıcı modelini (user) döner.
    """
    if not authorization or not authorization.startswith("Bearer "):
         raise HTTPException(status_code=401, detail="Valid 'Bearer' token required in Authorization header")
    
    token = authorization.split(" ")[1]
    
    try:
        response = supabase.auth.get_user(token)
        if not response or not response.user:
            raise HTTPException(status_code=401, detail="Token expired or invalid.")
        return response.user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")
