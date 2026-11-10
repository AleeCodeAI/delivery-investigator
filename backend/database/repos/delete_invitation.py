from database.models import Invitation 
from sqlalchemy.orm import Session
from sqlalchemy import delete
from database.engine import engine
from uuid import UUID 


def delete_invitation(access_key: UUID, email: str):
    """
    Deletes an invitation from invitation table which consequently deletes the user account and profile. Only admin is allowed for this operation.
    """
    try:
        with Session(engine) as session:
            statement = delete(Invitation).where(
                Invitation.access_key == access_key,
                Invitation.email == email
            )
            session.execute(statement)
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
