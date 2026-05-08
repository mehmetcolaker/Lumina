"""Celery background tasks for the execution (sandbox) module."""

import json
import logging

import redis as sync_redis
from celery import Celery

from app.core.config import settings
from app.core.database import sync_session_maker
from app.modules.execution.docker_service import run_code_in_sandbox, run_all_test_cases
from app.modules.execution.models import Submission, SubmissionStatus, SubmissionVerdict
from app.modules.courses.models import Step

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


def _determine_verdict(
    exit_code: int | None,
    timed_out: bool,
    stdout: str,
    expected_output: str | None,
    compare_mode: str = "trim",
) -> SubmissionVerdict:
    if timed_out:
        return SubmissionVerdict.TIMEOUT
    if exit_code is not None and exit_code != 0:
        return SubmissionVerdict.RUNTIME_ERROR

    if not expected_output:
        return SubmissionVerdict.PASS

    user_out = stdout.strip()
    expected = expected_output.strip()

    if compare_mode == "exact":
        return SubmissionVerdict.PASS if user_out == expected else SubmissionVerdict.WRONG_ANSWER
    elif compare_mode == "contains":
        return SubmissionVerdict.PASS if expected in user_out else SubmissionVerdict.WRONG_ANSWER
    elif compare_mode == "regex":
        import re
        return SubmissionVerdict.PASS if re.search(expected, user_out) else SubmissionVerdict.WRONG_ANSWER
    else:  # "trim" (default)
        return SubmissionVerdict.PASS if user_out == expected else SubmissionVerdict.WRONG_ANSWER


def _determine_test_verdict(test_results: list[dict]) -> SubmissionVerdict:
    """Overall verdict from test case results.

    - All pass -> PASS
    - Any timeout -> TIMEOUT
    - Any runtime error -> RUNTIME_ERROR
    - Any fail -> WRONG_ANSWER
    """
    if not test_results:
        return SubmissionVerdict.PASS

    has_timeout = any(r.get("stderr", "") and "(3 saniye" in r["stderr"] for r in test_results)
    has_error = any(not r["passed"] and r["stderr"] and "(3 saniye" not in r["stderr"] for r in test_results)
    has_fail = any(not r["passed"] for r in test_results)

    if has_timeout:
        return SubmissionVerdict.TIMEOUT
    if has_error:
        return SubmissionVerdict.RUNTIME_ERROR
    if has_fail:
        return SubmissionVerdict.WRONG_ANSWER

    return SubmissionVerdict.PASS


def _publish_result(
    submission_id: str,
    status: str,
    output: str | None = None,
    stdout: str | None = None,
    stderr: str | None = None,
    exit_code: int | None = None,
    runtime_ms: int | None = None,
    verdict: str | None = None,
    test_results: list[dict] | None = None,
) -> None:
    try:
        r = sync_redis.from_url(settings.REDIS_URL, socket_connect_timeout=3)
        channel = f"execution:result:{submission_id}"
        payload = json.dumps({
            "submission_id": submission_id,
            "status": status,
            "output": output,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "runtime_ms": runtime_ms,
            "verdict": verdict,
            "test_results": test_results,
        })
        r.publish(channel, payload)
        logger.info("Published result to channel %s", channel)
        r.close()
    except Exception as exc:
        logger.warning("Failed to publish result for %s to Redis: %s", submission_id, exc)


@celery_app.task(bind=True, max_retries=0, name="execute_user_code")
def execute_user_code(self, submission_id: str) -> dict:
    """Execute the code of a submission inside the sandbox."""
    from uuid import UUID

    session = sync_session_maker()
    try:
        submission = session.get(Submission, UUID(submission_id))
        if submission is None:
            logger.error("Submission %s not found", submission_id)
            return {"submission_id": submission_id, "status": "failed", "output": "Submission not found"}

        submission.status = SubmissionStatus.RUNNING
        session.commit()

        # Dil belirleme
        language = "python"
        step = None
        try:
            step = session.get(Step, submission.step_id)
            if step and step.section and step.section.course:
                language = step.section.course.language.lower()
        except Exception:
            pass

        try:
            result = run_code_in_sandbox(submission.code, language)

            stdout = result["stdout"]
            stderr = result["stderr"]
            exit_code = result["exit_code"]
            runtime_ms = result["runtime_ms"]
            timed_out = result["timed_out"]

            # Grading: expected_output
            expected_output = None
            compare_mode = "trim"
            test_cases = None
            try:
                if step is None:
                    step = session.get(Step, submission.step_id)
                if step and step.content_data:
                    expected_output = step.content_data.get("expected_output")
                    if isinstance(expected_output, str):
                        expected_output = expected_output.strip()
                    compare_mode = step.content_data.get("compare_mode", "trim")
                    test_cases = step.content_data.get("test_cases")
            except Exception:
                pass

            # Run test cases if available and no runtime error
            test_results = None
            if test_cases and isinstance(test_cases, list) and len(test_cases) > 0 and exit_code == 0 and not timed_out:
                test_results = run_all_test_cases(submission.code, language, test_cases)
                verdict = _determine_test_verdict(test_results)
            else:
                # Single expected_output grading (legacy mode)
                verdict = _determine_verdict(
                    exit_code=exit_code,
                    timed_out=timed_out,
                    stdout=stdout,
                    expected_output=expected_output,
                    compare_mode=compare_mode,
                )

            submission.status = SubmissionStatus.COMPLETED
            submission.output = stdout
            submission.stdout = stdout
            submission.stderr = stderr
            submission.exit_code = exit_code
            submission.runtime_ms = runtime_ms
            submission.verdict = verdict
            submission.test_results = json.dumps(test_results) if test_results else None

        except RuntimeError as exc:
            submission.status = SubmissionStatus.FAILED
            submission.output = str(exc)
            submission.stderr = str(exc)
        except Exception as exc:
            logger.exception("Unexpected error executing submission %s", submission_id)
            submission.status = SubmissionStatus.FAILED
            submission.output = f"Internal error: {exc}"
            submission.stderr = f"Internal error: {exc}"

        session.commit()

        logger.info(
            "Submission %s finished status=%s verdict=%s",
            submission_id,
            submission.status.value,
            submission.verdict.value if submission.verdict else "N/A",
        )

        _publish_result(
            submission_id,
            submission.status.value,
            output=submission.output,
            stdout=submission.stdout,
            stderr=submission.stderr,
            exit_code=submission.exit_code,
            runtime_ms=submission.runtime_ms,
            verdict=submission.verdict.value if submission.verdict else None,
            test_results=json.loads(submission.test_results) if submission.test_results else None,
        )

        return {
            "submission_id": submission_id,
            "status": submission.status.value,
            "output": submission.output,
            "stdout": submission.stdout,
            "stderr": submission.stderr,
            "exit_code": submission.exit_code,
            "runtime_ms": submission.runtime_ms,
            "verdict": submission.verdict.value if submission.verdict else None,
            "test_results": json.loads(submission.test_results) if submission.test_results else None,
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
