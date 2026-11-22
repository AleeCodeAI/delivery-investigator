from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from database.repos import check_invitation
from database.supabase_admin import get_supabase_admin
from schemas import SignUpData

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post("/sign-up/", status_code=201)
@limiter.limit("5/minute")
def endpoint_sign_up(request: Request, data: SignUpData):
    """Validate the invitation, then create the Supabase user."""
    email = data.email.strip().lower()

    try:
        access_key = UUID(data.access_key.strip())
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid invitation.")

    if not check_invitation(access_key=access_key, email=email):
        logger.warning(f"Rejected sign-up for {email}: invalid invitation")
        raise HTTPException(status_code=403, detail="Invalid invitation.")

    try:
        get_supabase_admin().auth.admin.create_user({
            "email": email,
            "password": data.password,
            "email_confirm": True,
            "user_metadata": {"full_name": data.full_name.strip()},
            "app_metadata": {"role": "operator"},
        })
    except Exception as e:
        logger.error(f"Supabase user creation failed for {email}: {e}")
        if "already" in str(e).lower():
            raise HTTPException(status_code=409, detail="An account with this email already exists.")
        raise HTTPException(status_code=500, detail="Failed to create account.")

    logger.info(f"Account created for {email}")
    return {"status": "success"}