"""PDF to JPG conversion."""
import zipfile
from pathlib import Path

import fitz

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.pdf_utils import render_preview


def _max_pages(job: ToolJob) -> int:
    if job.user and job.user.is_authenticated:
        try:
            profile = job.user.profile
            if profile.is_on_trial or (profile.plan and profile.plan.slug in ("pro", "business")):
                return 9999
        except Exception:
            pass
    return 1


def run(job: ToolJob, request=None) -> dict:
    src_rel = job.input_files[0]
    dpi = int(job.options.get("dpi", 150))
    src = file_handler.to_absolute(src_rel)
    doc = fitz.open(src)

    max_pages = min(_max_pages(job), doc.page_count)

    out_dir = file_handler.job_root(job.id) / "output" / "pages"
    out_dir.mkdir(parents=True, exist_ok=True)
    images = []

    for i in range(min(max_pages, doc.page_count)):
        page = doc[i]
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_path = out_dir / f"page_{i + 1}.jpg"
        pix.save(str(img_path))
        images.append(file_handler.to_relative(img_path))

    doc.close()

    if len(images) == 1:
        out_rel = images[0]
        preview = out_rel
    else:
        zip_path = file_handler.output_path(job, "pages.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            for img in images:
                zf.write(file_handler.to_absolute(img), Path(img).name)
        out_rel = file_handler.to_relative(zip_path)
        preview = images[0]

    return {
        "output_file": out_rel,
        "compression_stat": {"pages": len(images), "dpi": dpi},
        "preview_file": preview if out_rel.endswith(".jpg") else render_preview(job, images[0]) if images else "",
    }
