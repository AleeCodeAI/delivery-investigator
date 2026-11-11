from database.models import Invitation 
from sqlalchemy.orm import Session
from database.engine import engine 


def insert_invitation(
            name: str,
            email: str
    ):
    """
    Create and persist a new invitation for the specified name and email.
    The access key and creation timestamp are generated automatically.
    Raises an exception if the insertion fails.
    """
    
    with Session(engine) as session:
        try:
            invitation = Invitation(
                name=name,
                email=email
            )
            session.add(invitation)
            session.commit()
            return invitation.access_key
        
        except Exception as e:
            session.rollback()
            raise e
