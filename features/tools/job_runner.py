"""Run tool jobs without blocking the HTTP response (dev eager mode)."""
import logging
import threading

from django.conf import settings

from features.tools.tasks import process_tool

logger = logging.getLogger(__name__)


def _run_safe(job_id: int) -> None:
    try:
        process_tool(job_id)
    except Exception:
        logger.exception("Tool job %s failed in background thread", job_id)


def dispatch_tool_job(job_id: int) -> None:
    if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False):
        threading.Thread(target=_run_safe, args=(job_id,), daemon=True).start()
    else:
        process_tool.delay(job_id)
