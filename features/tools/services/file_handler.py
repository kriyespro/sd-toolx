"""File upload, validation, and job storage."""
import os
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

from features.tools.models import ToolJob
from features.tools.services.exceptions import FileValidationError


def job_root(job_id: int) -> Path:
    path = Path(settings.MEDIA_ROOT) / "jobs" / str(job_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def to_relative(path: Path) -> str:
    return str(path.relative_to(settings.MEDIA_ROOT))


def to_absolute(relative: str) -> Path:
    return Path(settings.MEDIA_ROOT) / relative


def validate_file(upload: UploadedFile, max_mb: int, allowed_ext: set[str]):
    if not upload.name:
        raise FileValidationError("File has no name.")
    ext = Path(upload.name).suffix.lower()
    if ext not in allowed_ext:
        raise FileValidationError(
            f"Invalid file type '{ext}'. Allowed: {', '.join(sorted(allowed_ext))}"
        )
    size_mb = upload.size / (1024 * 1024)
    if size_mb > max_mb:
        raise FileValidationError(f"File too large ({size_mb:.1f} MB). Max {max_mb} MB.")


def save_upload(job: ToolJob, upload: UploadedFile, index: int = 0) -> str:
    root = job_root(job.id) / "input"
    root.mkdir(parents=True, exist_ok=True)
    safe_name = f"{index}_{uuid.uuid4().hex[:8]}{Path(upload.name).suffix.lower()}"
    dest = root / safe_name
    with dest.open("wb") as f:
        for chunk in upload.chunks():
            f.write(chunk)
    return to_relative(dest)


def output_path(job: ToolJob, filename: str) -> Path:
    out = job_root(job.id) / "output" / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    return out


def download_url(request, relative_path: str) -> str:
    return request.build_absolute_uri(
        settings.MEDIA_URL + relative_path.replace("\\", "/")
    )


def file_size(relative_path: str) -> int:
    return to_absolute(relative_path).stat().st_size


def delete_job_files(job: ToolJob):
    root = Path(settings.MEDIA_ROOT) / "jobs" / str(job.id)
    if root.exists():
        for p in root.rglob("*"):
            if p.is_file():
                p.unlink()
        for p in sorted(root.rglob("*"), reverse=True):
            if p.is_dir():
                p.rmdir()
        try:
            root.rmdir()
        except OSError:
            pass
