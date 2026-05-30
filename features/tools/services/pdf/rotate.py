"""Rotate PDF pages."""
import fitz

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.pdf_utils import render_preview


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    angle = int(job.options.get("angle", 90))
    src = file_handler.to_absolute(src_rel)
    doc = fitz.open(src)

    for page in doc:
        page.set_rotation((page.rotation + angle) % 360)

    out = file_handler.output_path(job, "rotated.pdf")
    doc.save(str(out))
    doc.close()

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"angle": angle},
        "preview_file": render_preview(job, out_rel),
    }
