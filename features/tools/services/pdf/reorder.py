"""Reorder or delete PDF pages."""
import fitz

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.pdf_utils import render_preview


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    order = job.options.get("order") or []
    delete_pages = job.options.get("delete_pages") or []

    if isinstance(order, str):
        order = [int(x) for x in order.split(",") if x.strip().isdigit()]

    delete_set = set()
    for p in delete_pages:
        try:
            delete_set.add(int(p))
        except (TypeError, ValueError):
            pass

    src_doc = fitz.open(src)
    page_count = src_doc.page_count

    if order:
        indices = [i for i in order if 0 <= i < page_count and i not in delete_set]
    else:
        indices = [i for i in range(page_count) if i not in delete_set]

    if not indices:
        src_doc.close()
        raise ToolError("No pages left. Select at least one page.")

    out_doc = fitz.open()
    for i in indices:
        out_doc.insert_pdf(src_doc, from_page=i, to_page=i)
    src_doc.close()

    out = file_handler.output_path(job, "reordered.pdf")
    out_doc.save(str(out), garbage=4, deflate=True)
    out_doc.close()

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"pages": len(indices)},
        "preview_file": render_preview(job, out_rel),
    }
