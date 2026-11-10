from database.models import Profile
from sqlalchemy.orm import Session
from sqlalchemy import update
from database.engine import engine
from uuid import UUID


def update_role_to_admin(user_id: UUID, email: str) -> bool:
    """
    Updates an existing operator's role to admin. Only an existing admin is
    allowed for this operation.
    Returns True if a profile was updated, False if none matched.
    """
    with Session(engine) as session:
        try:
            statement = (
                update(Profile)
                .where(
                    Profile.user_id == user_id,
                    Profile.email == email,
                )
                .values(role="admin")
            )
            result = session.execute(statement)
            session.commit()
            return result.rowcount > 0
        except Exception:
            session.rollback()
            raise

if __name__ == "__main__":
    did_update = update_role_to_admin(
        user_id=UUID(""),
        email=""
    )
    print(did_update)