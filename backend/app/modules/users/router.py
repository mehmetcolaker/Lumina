from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.modules.users import services
from app.modules.users.schemas import Token, TokenPayload, UserCreate, UserResponse

router = APIRouter(prefix="/api/v1", tags=["Authentication & Users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Decode the JWT token and return the authenticated user.

    Args:
        token: The Bearer token extracted from the Authorization header.
        db: An async database session.

    Returns:
        The UserResponse for the authenticated user.

    Raises:
        HTTPException 401: If the token is invalid or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        user_id: str | None = token_data.sub
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = await services.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    return UserResponse.model_validate(user)


@router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> UserResponse:
    """Create a new user account.

    The email must be unique. Returns the created user profile.
    """
    try:
        user = await services.create_user(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    return UserResponse.model_validate(user)


@router.post(
    "/auth/login",
    response_model=Token,
    summary="Login and obtain an access token",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Authenticate with email and password, receiving a JWT access token.

    Standard OAuth2 password flow: pass `username` (the email) and `password`
    as form fields.
    """
    user = await services.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@router.get(
    "/users/me",
    response_model=UserResponse,
    summary="Get the currently authenticated user",
)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    return current_user
