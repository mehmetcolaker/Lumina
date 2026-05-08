from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.gamification import services
from app.modules.gamification.schemas import (
    BadgeResponse,
    CommentCreate,
    CommentResponse,
    LeaderboardEntry,
    LeaderboardResponse,
    UserBadgesResponse,
)
from app.modules.users.router import get_current_user
from app.modules.users.schemas import UserResponse

router = APIRouter(prefix="/api/v1/gamification", tags=["Gamification"])


@router.get(
    "/leaderboard",
    response_model=LeaderboardResponse,
    summary="Get the global XP leaderboard",
)
async def get_leaderboard(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
) -> LeaderboardResponse:
    """Return the top-N users sorted by total experience points.

    The data is served from Redis via ``ZREVRANGE`` for near-instant
    response.  Falls back to PostgreSQL if Redis is unavailable.

    Args:
        limit: Maximum number of entries to return (default 10, max 100).
    """
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="limit must be between 1 and 100.",
        )

    entries_data = await services.get_leaderboard(db, limit=limit)
    entries = [LeaderboardEntry(**e) for e in entries_data]
    return LeaderboardResponse(entries=entries)


@router.post(
    "/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a comment to a code line",
)
async def add_comment(
    payload: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> CommentResponse:
    """Attach a comment to a specific line of code within a step."""
    comment = await services.add_comment(
        db,
        user_id=current_user.id,
        step_id=payload.step_id,
        line_number=payload.line_number,
        content=payload.content,
    )
    return CommentResponse(
        id=comment.id,
        step_id=comment.step_id,
        user_id=comment.user_id,
        email=current_user.email,
        line_number=comment.line_number,
        content=comment.content,
        created_at=comment.created_at,
    )


@router.get(
    "/comments/{step_id}",
    response_model=list[CommentResponse],
    summary="Get all comments for a step",
)
async def get_comments(
    step_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[CommentResponse]:
    """Return every comment attached to the given step.

    Results are ordered by ``line_number`` ascending and then by
    ``created_at``, so the front-end can render them beside the
    corresponding code lines.
    """
    try:
        step_uuid = UUID(step_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid step_id format.",
        )

    comments_data = await services.get_comments_for_step(db, step_uuid)
    return [CommentResponse(**c) for c in comments_data]


@router.get(
    "/badges",
    response_model=UserBadgesResponse,
    summary="Get all badges for the current user",
)
async def get_badges(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> UserBadgesResponse:
    """Return all badges (owned + available) for the authenticated user."""
    owned_badges = await services.get_user_badges(db, current_user.id)
    all_defs = await services.get_all_badge_definitions()

    owned_set = {b.badge_type for b in owned_badges}

    owned_list: list[BadgeResponse] = []
    locked_list: list[BadgeResponse] = []

    for b in owned_badges:
        owned_list.append(
            BadgeResponse(
                badge_type=b.badge_type,
                title=b.title,
                emoji=b.emoji,
                description=b.description,
                earned_at=b.earned_at,
                owned=True,
            )
        )

    for d in all_defs:
        if d["type"] not in owned_set:
            locked_list.append(
                BadgeResponse(
                    badge_type=d["type"],
                    title=d["title"],
                    emoji=d["emoji"],
                    description=d["desc"],
                    owned=False,
                )
            )

    return UserBadgesResponse(owned=owned_list, locked=locked_list)
