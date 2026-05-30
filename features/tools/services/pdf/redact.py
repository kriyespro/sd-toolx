"""Redact text in a PDF (permanent black-box redaction)."""
import fitz

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.pdf_utils import render_preview


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    search_terms = job.options.get("search_terms", "")
    out = file_handler.output_path(job, "redacted.pdf")

    if not search_terms:
        raise ToolError("No search terms provided. Enter text to redact.")

    terms = [t.strip() for t in search_terms.split("\n") if t.strip()]
    if not terms:
        raise ToolError("No valid search terms.")

    doc = fitz.open(str(src))
    total_redacted = 0

    for page in doc:
        for term in terms:
            areas = page.search_for(term)
            for rect in areas:
                page.add_redact_annot(rect, fill=(0, 0, 0))
                total_redacted += 1
        page.apply_redactions()

    doc.save(str(out), garbage=4, deflate=True)
    doc.close()

    if total_redacted == 0:
        raise ToolError("No matching text found to redact. Check your search terms.")

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"redactions_applied": total_redacted},
        "preview_file": render_preview(job, out_rel),
    }
