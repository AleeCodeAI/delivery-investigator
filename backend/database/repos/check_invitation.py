from database.models import Invitation
from sqlalchemy.orm import Session
from sqlalchemy import select
from database.engine import engine
from uuid import UUID


def check_invitation(access_key: UUID, email: str) -> bool:
    """
    Checks if an invitation is valid.
    """
    with Session(engine) as session:
        try:
            statement = select(Invitation).where(
                Invitation.access_key == access_key,
                Invitation.email == email,
            )
            result = session.scalars(statement).one_or_none()
            return True if result else False
        except Exception:
            session.rollback()
            raise

if __name__ == "__main__":
    is_invitation = check_invitation(
        access_key= UUID("402e73b9-8fb2-4d22-89d4-f68244fe9c10"),
        email="aleetest16@gmail.com"
    )
    print(is_invitation)