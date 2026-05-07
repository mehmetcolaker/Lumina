"""Celery background tasks for the execution (sandbox) module.

Workflow
--------
1. FastAPI router creates a ``Submission`` record (status = ``pending``)
   and calls ``execute_user_code.delay(submission_id)``.
2. Celery worker picks up the task, sets status → ``running``, calls
   the Docker sandbox, and stores the output.

Start the Celery worker with::

    celery -A app.modules.execution.tasks.celery_app worker --loglevel=info --pool=solo

.. note::
    The ``--pool=solo`` flag is required on Windows where ``prefork`` is
    not supported. On Linux/macOS you may omit it or use ``--pool=gevent``.
"""

import logging

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


@celery_app.task(bind=True, max_retries=0, name="execute_user_code")
def execute_user_code(self, submission_id: str) -> dict:
    """Execute the code of a submission inside the Docker sandbox.

    Retrieves the ``Submission`` record, updates its status to ``running``,
    calls :func:`run_code_in_docker`, and persists the result.

    Args:
        submission_id: The UUID (as string) of the Submission to execute.

    Returns:
        A dict with keys ``submission_id``, ``status``, and ``output``.
    """
    from uuid import UUID

    session = sync_session_maker()
    try:
        submission = session.get(Submission, UUID(submission_id))
        if submission is None:
            logger.error("Submission %s not found", submission_id)
            return {"submission_id": submission_id, "status": "failed", "output": "Submission not found"}

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
            logger.exception("Unexpected error executing submission %s", submission_id)
            submission.status = SubmissionStatus.FAILED
            submission.output = f"Internal error: {exc}"

        session.commit()

        logger.info(
            "Submission %s finished with status=%s",
            submission_id,
            submission.status.value,
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
