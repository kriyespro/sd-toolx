"""Repair/recover a corrupt or broken PDF."""
import fitz

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.pdf_utils import render_preview


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    out = file_handler.output_path(job, "repaired.pdf")

    try:
        doc = fitz.open(str(src))
    except Exception as exc:
        raise ToolError(f"Cannot open file: {exc}") from exc

    if doc.page_count == 0:
        doc.close()
        raise ToolError("PDF has no pages — may be too damaged to repair.")

    doc.save(str(out), garbage=4, deflate=True, clean=True)
    pages = doc.page_count
    doc.close()

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"pages_recovered": pages},
        "preview_file": render_preview(job, out_rel),
    }
