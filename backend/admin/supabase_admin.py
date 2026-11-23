from functools import lru_cache
from supabase import Client, create_client
from configs.settings import get_settings


@lru_cache()
def get_supabase_admin() -> Client:
    """Admin client (secret key). Backend use only."""
    db = get_settings().database
    if not db.supabase_project_url or not db.supabase_secret_key:
        raise RuntimeError("SUPABASE_PROJECT_URL and SUPABASE_SECRET_KEY must be set.")
    return create_client(db.supabase_project_url, db.supabase_secret_key)


def get_supabase_public() -> Client:
    """Public client (publishable key). New client per call, so no session
    is shared between users."""
    db = get_settings().database
    if not db.supabase_project_url or not db.supabase_publishable_key:
        raise RuntimeError("SUPABASE_PROJECT_URL and SUPABASE_PUBLISHABLE_KEY must be set.")
    return create_client(db.supabase_project_url, db.supabase_publishable_key)