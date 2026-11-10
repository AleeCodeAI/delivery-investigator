from database.models import Invitation
from sqlalchemy.orm import Session
from sqlalchemy import delete
from database.engine import engine
from uuid import UUID


def delete_invitation(access_key: UUID, email: str) -> bool:
    """
    Deletes an invitation from the invitation table, which consequently deletes
    the user account and profile. Only admin is allowed for this operation.
    Returns True if an invitation was deleted, False if none matched.
    """
    with Session(engine) as session:
        try:
            statement = delete(Invitation).where(
                Invitation.access_key == access_key,
                Invitation.email == email,
            )
            result = session.execute(statement)
            session.commit()
            return result.rowcount > 0
        except Exception:
            session.rollback()
            raise

if __name__ == "__main__":
    did_delete = delete_invitation(
        access_key= UUID("bcd9c428-4988-4c0e-854f-4bbefd1fe33c"),
        email="aleghui224@yahoo.com"
    )
    print(did_delete)