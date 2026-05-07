"""Celery background tasks for the execution (sandbox) module.

Workflow
--------
1. FastAPI router creates a ``Submission`` record (status = ``pending``)
   and calls ``execute_user_code.delay(submission_id)``.
2. Celery worker picks up the task, sets status → ``running``, calls
   the Docker sandbox, and stores the output.
3. After persisting the result the worker **publishes** the outcome to
   a Redis Pub/Sub channel so that any WebSocket listener can forward it
   to the client in real time.

Start the Celery worker with::

    celery -A app.modules.execution.tasks.celery_app worker --loglevel=info --pool=solo

.. note::
    The ``--pool=solo`` flag is required on Windows where ``prefork`` is
    not supported. On Linux/macOS you may omit it or use ``--pool=gevent``.
"""

import json
import logging

import redis as sync_redis
from celery import Celery

from app.core.config import settings
from app.core.database import sync_session_maker
from app.modules.execution.docker_service import run_code_in_docker
from app.modules.execution.models import Submission, SubmissionStatus

logger = logging.getLogger(__name__)

celery_app = Celery(
    "lumina_execution",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


def _publish_result(submission_id: str, status: str, output: str | None) -> None:
    """Publish the execution result to a Redis Pub/Sub channel.

    The channel name follows the convention ``execution:result:<submission_id>``
    so that the FastAPI WebSocket handler can subscribe and relay the
    message to the connected client.

    Args:
        submission_id: The UUID string of the submission.
        status: One of ``completed`` / ``failed``.
        output: The combined stdout + stderr / error message.
    """
    try:
        r = sync_redis.from_url(settings.REDIS_URL, socket_connect_timeout=3)
        channel = f"execution:result:{submission_id}"
        payload = json.dumps(
            {
                "submission_id": submission_id,
                "status": status,
                "output": output,
            }
        )
        r.publish(channel, payload)
        logger.info("Published result to channel %s", channel)
        r.close()
    except Exception as exc:
        logger.warning(
            "Failed to publish result for %s to Redis: %s",
            submission_id,
            exc,
        )


@celery_app.task(bind=True, max_retries=0, name="execute_user_code")
def execute_user_code(self, submission_id: str) -> dict:
    """Execute the code of a submission inside the Docker sandbox.

    Retrieves the ``Submission`` record, updates its status to ``running``,
    calls :func:`run_code_in_docker`, persists the result, and publishes
    the outcome via Redis Pub/Sub so that any waiting WebSocket client is
    notified immediately.
    """
    from uuid import UUID

    session = sync_session_maker()
    try:
        submission = session.get(Submission, UUID(submission_id))
        if submission is None:
            logger.error("Submission %s not found", submission_id)
            _publish_result(submission_id, "failed", "Submission not found")
            return {
                "submission_id": submission_id,
                "status": "failed",
                "output": "Submission not found",
            }

        # Mark as running
        submission.status = SubmissionStatus.RUNNING
        session.commit()

        # Infer language from the step … for now, default to "python"
        language = "python"

        try:
            output = run_code_in_docker(submission.code, language)
            submission.status = SubmissionStatus.COMPLETED
            submission.output = output
        except RuntimeError as exc:
            submission.status = SubmissionStatus.FAILED
            submission.output = str(exc)
        except Exception as exc:
            logger.exception(
                "Unexpected error executing submission %s", submission_id
            )
            submission.status = SubmissionStatus.FAILED
            submission.output = f"Internal error: {exc}"

        session.commit()

        logger.info(
            "Submission %s finished with status=%s",
            submission_id,
            submission.status.value,
        )

        # Publish result to Redis Pub/Sub for real-time delivery
        _publish_result(
            submission_id,
            submission.status.value,
            submission.output,
        )

        return {
            "submission_id": submission_id,
            "status": submission.status.value,
            "output": submission.output,
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
