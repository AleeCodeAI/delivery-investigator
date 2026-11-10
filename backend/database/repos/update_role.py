from database.models import Profile 
from sqlalchemy.orm import Session
from sqlalchemy import update
from database.engine import engine
from uuid import UUID 


def update_role_to_admin(user_id: UUID, email: str):
    """
    Updates an existing operator's role to admin. Only existing admin is allowed for this operation.
    """
    try:
        with Session(engine) as session:
            statement = update(Profile).where(
                Profile.user_id == user_id,
                Profile.email == email
            ).values(role = "admin")
            session.execute(statement)
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
