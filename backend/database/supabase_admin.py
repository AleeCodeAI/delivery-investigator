from functools import lru_cache
from supabase import Client, create_client
from configs.settings import get_settings


@lru_cache()
def get_supabase_admin() -> Client:
    """Cached Supabase client with admin rights (secret key). Backend use only."""
    db = get_settings().database
    if not db.supabase_url or not db.supabase_secret_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SECRET_KEY must be set.")
    return create_client(db.supabase_project_url, db.supabase_secret_key)