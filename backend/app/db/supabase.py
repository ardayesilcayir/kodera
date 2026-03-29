from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger("uvicorn.error")

# Supabase istemcisini başlat
try:
    if not settings.SUPABASE_URL or "your-project" in settings.SUPABASE_URL:
        logger.warning("Supabase URL is not configured properly. DB features may fail.")
        supabase = None
    else:
        supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    supabase = None
