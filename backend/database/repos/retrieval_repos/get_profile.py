from sqlalchemy import select
from sqlalchemy.orm import Session
from database.engine import engine
from database.models import Profile
from schemas import ProfileSchema
from uuid import UUID


def get_profile(user_id: UUID) -> ProfileSchema:
    """
    Retrieve a user's profile details by their ID.

    Args:
        user_id (UUID): The unique ID of the user whose profile to retrieve.

    Returns:
        A ProfileSchema object containing the user's profile details.

    Raises:
        LookupError: If the user's profile is not found.
    """
    with Session(engine) as session:
        statement = select(Profile).where(
            Profile.user_id == user_id
        )
        profile_row = session.scalars(statement).one_or_none()

        if profile_row is None:
            raise LookupError(f"Profile for user: {user_id} not found.")

        return ProfileSchema(
            user_id=profile_row.user_id,
            name=profile_row.name,
            email=profile_row.email,
            role=profile_row.role,
            created_at=profile_row.created_at,
        )


if __name__ == "__main__":
    result = get_profile(user_id=UUID("2f4ba39a-abc7-482c-9481-df8a02c36c5d"))
    print(result)
