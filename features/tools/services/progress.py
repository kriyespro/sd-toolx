"""Job progress updates for HTMX polling."""
from features.tools.models import ToolJob


def set_progress(job: ToolJob, pct: int, stage: str = "") -> None:
    stat = dict(job.compression_stat or {})
    stat["progress"] = min(100, max(0, int(pct)))
    if stage:
        stat["stage"] = stage
    job.compression_stat = stat
    job.save(update_fields=["compression_stat"])
