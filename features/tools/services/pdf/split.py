"""Split PDF by page ranges."""
import fitz

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.pdf_utils import render_preview


def _parse_pages(spec: str, page_count: int) -> list[int]:
    """Parse '1-3,5,7' into 0-based page indices."""
    pages = set()
    for part in spec.replace(" ", "").split(","):
        if not part:
            continue
        try:
            if "-" in part:
                a, b = part.split("-", 1)
                start = max(1, int(a))
                end = min(page_count, int(b))
                pages.update(range(start - 1, end))
            else:
                p = int(part) - 1
                if 0 <= p < page_count:
                    pages.add(p)
        except (ValueError, TypeError):
            continue
    return sorted(pages)


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    doc = fitz.open(src)
    page_count = doc.page_count

    mode = job.options.get("mode", "range")
    if mode == "all":
        indices = list(range(page_count))
    else:
        spec = job.options.get("pages", "1")
        indices = _parse_pages(spec, page_count)

    if not indices:
        doc.close()
        raise ToolError("No valid pages selected.")

    out_doc = fitz.open()
    for i in indices:
        out_doc.insert_pdf(doc, from_page=i, to_page=i)
    doc.close()

    out = file_handler.output_path(job, "split.pdf")
    out_doc.save(str(out))
    out_doc.close()

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"pages_extracted": len(indices)},
        "preview_file": render_preview(job, out_rel),
    }
