from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from database.repos import check_invitation
from admin.supabase_admin import get_supabase_admin, get_supabase_public
from schemas import SignUpData
from configs.settings import get_settings

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

# must be in Supabase: Authentication -> URL Configuration -> Redirect URLs
EMAIL_REDIRECT_URL = get_settings().frontend.frontend_url


class ResendData(BaseModel):
    email: EmailStr


@router.post("/sign-up/", status_code=201)
@limiter.limit("5/minute")
def endpoint_sign_up(request: Request, data: SignUpData):
    """Validate the invitation, create the user, send the confirmation email."""
    email = data.email.strip().lower()

    try:
        access_key = UUID(data.access_key.strip())
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid invitation.")

    if not check_invitation(access_key=access_key, email=email):
        logger.warning(f"Rejected sign-up for {email}: invalid invitation")
        raise HTTPException(status_code=403, detail="Invalid invitation.")

    # 1. Create the user as UNCONFIRMED
    try:
        get_supabase_admin().auth.admin.create_user({
            "email": email,
            "password": data.password,
            "email_confirm": False,
            "user_metadata": {"full_name": data.full_name.strip()},
            "app_metadata": {"role": "operator"},
        })
    except Exception as e:
        logger.error(f"Supabase user creation failed for {email}: {e}")
        if "already" in str(e).lower():
            raise HTTPException(status_code=409, detail="An account with this email already exists.")
        raise HTTPException(status_code=500, detail="Failed to create account.")

    # 2. Ask Supabase to send the confirmation email (goes through Brevo)
    try:
        get_supabase_public().auth.resend({
            "type": "signup",
            "email": email,
            "options": {"email_redirect_to": EMAIL_REDIRECT_URL},
        })
    except Exception as e:
        # the account exists, so don't fail the request; the user can resend
        logger.error(f"Confirmation email failed for {email}: {e}")
        return {"status": "created_email_failed"}

    logger.info(f"Account created for {email}, confirmation email sent")
    return {"status": "check_email"}


@router.post("/resend-confirmation/")
@limiter.limit("3/minute")
def endpoint_resend_confirmation(request: Request, data: ResendData):
    """Resend the confirmation email. Always returns the same response,
    so it can't be used to find out which emails have accounts."""
    email = data.email.strip().lower()
    try:
        get_supabase_public().auth.resend({
            "type": "signup",
            "email": email,
            "options": {"email_redirect_to": EMAIL_REDIRECT_URL},
        })
    except Exception as e:
        logger.error(f"Resend failed for {email}: {e}")
    return {"status": "ok"}