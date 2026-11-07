from sqlalchemy import Column, Table, UUID
from database.base import Base

auth_users = Table(
    "users",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    schema="auth",
)

"""
Represents Supabase's existing auth.users table in SQLAlchemy metadata
so application models can reference its user IDs through foreign keys.
The actual table is managed by Supabase and is not created by SQLAlchemy.
This is created to solve the profile's table creation problem with foreign key constraints to auth.users table.
"""