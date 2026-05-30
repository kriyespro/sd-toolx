"""Shared PDF helpers."""
import fitz

from features.tools.services import file_handler


def render_preview(job, pdf_relative: str, max_width: int = 200) -> str:
    """Render first page thumbnail for preview."""
    src = file_handler.to_absolute(pdf_relative)
    doc = fitz.open(src)
    if doc.page_count == 0:
        doc.close()
        return ""
    page = doc[0]
    zoom = max_width / page.rect.width
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    preview = file_handler.output_path(job, "preview.jpg")
    pix.save(str(preview))
    doc.close()
    return file_handler.to_relative(preview)


def compression_stats(original_path: str, output_path: str) -> dict:
    orig = file_handler.file_size(original_path)
    new = file_handler.file_size(output_path)
    if orig == 0:
        saved_pct = 0
    else:
        saved_pct = max(0, round((1 - new / orig) * 100))
    return {
        "original_bytes": orig,
        "output_bytes": new,
        "saved_pct": saved_pct,
    }
