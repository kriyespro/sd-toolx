from celery import shared_task
from django.utils import timezone

from features.tools.models import ToolJob
from features.tools.services.handlers import run_handler
from features.tools.services.progress import set_progress


@shared_task(queue="default")
def process_tool(job_id: int):
    job = ToolJob.objects.get(pk=job_id)
    job.status = ToolJob.STATUS_PROCESSING
    set_progress(job, 5, "Upload received…")

    try:
        set_progress(job, 12, "Preparing…")
        result = run_handler(job)
        set_progress(job, 92, "Saving result…")

        job.output_file = result.get("output_file", "")
        job.preview_file = result.get("preview_file", "")
        job.compression_stat = {**result.get("compression_stat", {}), "progress": 100, "stage": "Complete"}
        job.status = ToolJob.STATUS_DONE
        job.save(
            update_fields=["output_file", "preview_file", "compression_stat", "status"]
        )
    except Exception as exc:
        from features.tools.services.exceptions import ToolError

        job.status = ToolJob.STATUS_FAILED
        job.error_message = (
            exc.message if isinstance(exc, ToolError) and hasattr(exc, "message") else str(exc)
        )
        job.compression_stat = {"progress": 0, "stage": "Failed"}
        job.save(update_fields=["status", "error_message", "compression_stat"])


@shared_task(queue="default")
def purge_expired_jobs():
    now = timezone.now()
    ToolJob.objects.filter(expires_at__lt=now).delete()
