from sqlalchemy import select
from sqlalchemy.orm import Session
from database.engine import engine
from database.models import Invitation
from schemas import InvitationSchema


def get_invitations():
    """
    Retrieve all invitations from the database.

    Returns:
        List[InvitationSchema]: A list of invitation records.
    """
    with Session(engine) as session:
        statement = select(Invitation)
        invitation_rows = session.scalars(statement).all()

        if invitation_rows is None:
            return []
        
        invitations = [
            InvitationSchema(
                access_key=row.access_key,
                name=row.name,
                email=row.email,
                created_at=row.created_at
            )
            for row in invitation_rows
        ]

        return invitations

if __name__ == "__main__":
    invitations = get_invitations()
    for invitation in invitations:
        print(invitation)