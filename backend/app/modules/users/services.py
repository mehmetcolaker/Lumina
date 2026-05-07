from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate


async def create_user(db: AsyncSession, payload: UserCreate) -> User:
    """Register a new user account.

    Checks for email uniqueness before inserting the new record.

    Args:
        db: An async database session.
        payload: The validated registration data (email + password).

    Returns:
        The newly created User ORM instance.

    Raises:
        ValueError: If a user with the given email already exists.
    """
    existing = await get_user_by_email(db, payload.email)
    if existing:
        raise ValueError(f"A user with email '{payload.email}' already exists.")

    hashed_pw = hash_password(payload.password)
    user = User(email=payload.email, hashed_password=hashed_pw)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """Authenticate a user by email and password.

    Args:
        db: An async database session.
        email: The user's email address.
        password: The raw password to verify.

    Returns:
        The User instance if credentials are valid, None otherwise.
    """
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Retrieve a user by email address.

    Args:
        db: An async database session.
        email: The email address to look up.

    Returns:
        The User instance if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """Retrieve a user by their UUID string.

    Args:
        db: An async database session.
        user_id: The UUID string of the user.

    Returns:
        The User instance if found, None otherwise.
    """
    from uuid import UUID

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    return result.scalar_one_or_none()
