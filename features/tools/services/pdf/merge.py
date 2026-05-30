"""Merge multiple PDFs, then compress the result."""
import fitz

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.pdf.compress import compress_path
from features.tools.services.pdf_utils import render_preview
from features.tools.services.progress import set_progress


def run(job: ToolJob) -> dict:
    order = job.options.get("order", list(range(len(job.input_files))))
    quality = job.options.get("quality", "medium")
    set_progress(job, 18, "Merging PDFs…")
    merged = fitz.open()

    for idx in order:
        if idx >= len(job.input_files):
            continue
        src = file_handler.to_absolute(job.input_files[idx])
        doc = fitz.open(src)
        merged.insert_pdf(doc)
        doc.close()

    if merged.page_count == 0:
        merged.close()
        raise ToolError("No pages to merge. Upload at least 2 valid PDF files.")

    merged_raw = file_handler.output_path(job, "_merged_raw.pdf")
    merged.save(str(merged_raw), garbage=4, deflate=True)
    merged.close()

    out = file_handler.output_path(job, "merged-compressed.pdf")
    compress_stats = compress_path(merged_raw, out, quality, job)

    merged_raw.unlink(missing_ok=True)

    out_rel = file_handler.to_relative(out)
    check = fitz.open(file_handler.to_absolute(out_rel))
    page_count = check.page_count
    check.close()

    stats = {
        **compress_stats,
        "pages": page_count,
        "files_merged": len(order),
    }

    return {
        "output_file": out_rel,
        "compression_stat": stats,
        "preview_file": render_preview(job, out_rel),
    }
