import asyncio
import json
import logging
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import async_session_maker, get_db
from app.core.redis_client import get_redis
from app.modules.execution import tasks
from app.modules.execution.connection_manager import manager
from app.modules.execution.models import Submission, SubmissionStatus
from app.modules.execution.schemas import (
    CodeSubmitRequest,
    CodeSubmitResponse,
    SubmissionStatusResponse,
)
from app.modules.users.router import get_current_user
from app.modules.users.schemas import TokenPayload, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/execution", tags=["Execution (Sandbox)"])

# Timeout after which an unanswered WebSocket connection is closed.
WS_TIMEOUT_SECONDS = 120


# ------------------------------------------------------------------
# HTTP endpoints
# ------------------------------------------------------------------


@router.post(
    "/submit",
    response_model=CodeSubmitResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit user code for sandboxed execution",
)
async def submit_code(
    payload: CodeSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> CodeSubmitResponse:
    """Accept user code, create a pending ``Submission`` record, and
    enqueue a Celery task to run it in an isolated sandbox.

    After submitting, the front-end can either poll via
    ``GET /status/{submission_id}`` or connect via
    ``ws://host/api/v1/execution/ws/{submission_id}?token=...``
    for a real-time result.
    """
    submission = Submission(
        user_id=current_user.id,
        step_id=payload.step_id,
        code=payload.code,
        status=SubmissionStatus.PENDING,
    )
    db.add(submission)
    await db.flush()
    await db.refresh(submission)

    tasks.execute_user_code.delay(str(submission.id))

    return CodeSubmitResponse(
        submission_id=submission.id,
        status=submission.status.value,
    )


@router.get(
    "/status/{submission_id}",
    response_model=SubmissionStatusResponse,
    summary="Poll the execution status of a submission",
)
async def get_submission_status(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> SubmissionStatusResponse:
    """Return the current status and output (if finished) of a code
    submission.  Falls back to polling when WebSocket is unavailable.
    """
    try:
        sub_id = UUID(submission_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid submission_id format.",
        )

    result = await db.execute(select(Submission).where(Submission.id == sub_id))
    submission = result.scalar_one_or_none()

    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found.",
        )

    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own submissions.",
        )

    return SubmissionStatusResponse(
        submission_id=submission.id,
        status=submission.status.value,
        output=submission.output,
        stdout=submission.stdout,
        stderr=submission.stderr,
        exit_code=submission.exit_code,
        runtime_ms=submission.runtime_ms,
        verdict=submission.verdict.value if submission.verdict else None,
    )


@router.get(
    "/submissions",
    summary="List recent submissions for a step",
)
async def list_submissions(
    step_id: str = Query(..., description="Filter by step UUID"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> list[SubmissionStatusResponse]:
    """Return the most recent submissions for a given step by the
    current user.
    """
    try:
        step_uuid = UUID(step_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid step_id format.")

    result = await db.execute(
        select(Submission)
        .where(
            Submission.user_id == current_user.id,
            Submission.step_id == step_uuid,
        )
        .order_by(Submission.created_at.desc())
        .limit(limit)
    )
    submissions = result.scalars().all()

    return [
        SubmissionStatusResponse(
            submission_id=s.id,
            status=s.status.value,
            output=s.output,
            stdout=s.stdout,
            stderr=s.stderr,
            exit_code=s.exit_code,
            runtime_ms=s.runtime_ms,
            verdict=s.verdict.value if s.verdict else None,
        )
        for s in submissions
    ]


# ------------------------------------------------------------------
# WebSocket endpoint
# ------------------------------------------------------------------


def _decode_ws_token(token: str) -> UUID | None:
    """Validate a JWT sent as a WebSocket query parameter.

    Args:
        token: The raw JWT string.

    Returns:
        The authenticated user's UUID, or None if the token is invalid.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            return None
        return UUID(token_data.sub)
    except (jwt.PyJWTError, ValueError):
        return None


@router.websocket(
    "/ws/{submission_id}",
)
async def execution_websocket(
    websocket: WebSocket,
    submission_id: str,
    token: str = Query(...),
):
    """Real-time code execution result via WebSocket.

    The client sends a **single** WebSocket upgrade request including a
    ``token`` query parameter (a valid JWT).  The server authenticates the
    user, verifies the submission belongs to them, and then listens for
    the result on a Redis Pub/Sub channel.

    **Protocol:**:

        1. Connect::
            ws://host/api/v1/execution/ws/{submission_id}?token=<JWT>

        2. Receive (JSON)::
            {
              "submission_id": "...",
              "status": "completed/failed",
              "output": "...",
              "stdout": "...",
              "stderr": "...",
              "exit_code": 0,
              "runtime_ms": 142,
              "verdict": "pass"
            }

        3. Server closes the connection.

    If the result is already in the database it is sent immediately.
    Otherwise the server waits for up to ``WS_TIMEOUT_SECONDS`` (120 s).
    """
    # ---- 1. Authenticate via JWT ----
    user_id = _decode_ws_token(token)
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # ---- 2. Validate submission_id ----
    try:
        sub_uuid = UUID(submission_id)
    except ValueError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # ---- 3. Verify ownership ----
    async with async_session_maker() as ws_db:
        result = await ws_db.execute(
            select(Submission).where(Submission.id == sub_uuid)
        )
        submission = result.scalar_one_or_none()

        if submission is None or submission.user_id != user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Result already available → send immediately
        if submission.status in (
            SubmissionStatus.COMPLETED,
            SubmissionStatus.FAILED,
        ):
            await websocket.accept()
            await websocket.send_text(
                json.dumps(
                    {
                        "submission_id": submission_id,
                        "status": submission.status.value,
                        "output": submission.output,
                        "stdout": submission.stdout,
                        "stderr": submission.stderr,
                        "exit_code": submission.exit_code,
                        "runtime_ms": submission.runtime_ms,
                        "verdict": submission.verdict.value if submission.verdict else None,
                    }
                )
            )
            await websocket.close()
            return

    # ---- 4. Register and listen on Redis Pub/Sub ----
    await manager.connect(websocket, submission_id)
    channel = f"execution:result:{submission_id}"
    pubsub = None

    try:
        redis = get_redis()
        pubsub = redis.pubsub()
        await pubsub.subscribe(channel)

        async def _listen() -> dict:
            while True:
                msg = await pubsub.get_message(
                    timeout=1.0, ignore_subscribe_messages=True
                )
                if msg is not None and msg["type"] == "message":
                    raw = msg["data"]
                    if isinstance(raw, bytes):
                        raw = raw.decode("utf-8")
                    return json.loads(raw)

        try:
            result_data = await asyncio.wait_for(
                _listen(), timeout=WS_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            result_data = {
                "submission_id": submission_id,
                "status": "timeout",
                "output": "Execution result did not arrive in time.",
            }

        try:
            await websocket.send_text(json.dumps(result_data))
        except Exception:
            pass  # client already gone

    except RuntimeError:
        logger.warning("Redis unavailable for WS — sending fallback")
        try:
            await websocket.send_text(
                json.dumps(
                    {
                        "submission_id": submission_id,
                        "status": "error",
                        "output": "Real-time delivery unavailable. Please poll /status.",
                    }
                )
            )
        except Exception:
            pass
    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("WebSocket error for submission %s", submission_id)
    finally:
        await manager.disconnect(websocket, submission_id)
        if pubsub is not None:
            try:
                await pubsub.unsubscribe(channel)
                await pubsub.close()
            except Exception:
                pass
