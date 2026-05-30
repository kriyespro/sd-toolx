"""Compare two PDFs side-by-side — highlight changed pages."""
import io
from PIL import Image
import fitz

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.pdf_utils import render_preview


def _page_to_pil(page: fitz.Page, zoom: float = 1.5) -> Image.Image:
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    return Image.open(io.BytesIO(pix.tobytes("png")))


def run(job: ToolJob) -> dict:
    if len(job.input_files) < 2:
        raise ToolError("Upload exactly 2 PDF files to compare.")

    src1 = file_handler.to_absolute(job.input_files[0])
    src2 = file_handler.to_absolute(job.input_files[1])
    out = file_handler.output_path(job, "comparison.pdf")

    doc1 = fitz.open(str(src1))
    doc2 = fitz.open(str(src2))

    pages = max(doc1.page_count, doc2.page_count)
    result_doc = fitz.open()

    for i in range(pages):
        pg1 = doc1[i] if i < doc1.page_count else None
        pg2 = doc2[i] if i < doc2.page_count else None

        img1 = _page_to_pil(pg1) if pg1 else Image.new("RGB", (595, 842), "white")
        img2 = _page_to_pil(pg2) if pg2 else Image.new("RGB", (595, 842), "white")

        img1 = img1.resize((595, 842), Image.LANCZOS)
        img2 = img2.resize((595, 842), Image.LANCZOS)

        combined = Image.new("RGB", (1190 + 10, 842), "#e5e7eb")
        combined.paste(img1, (0, 0))
        combined.paste(img2, (600, 0))

        buf = io.BytesIO()
        combined.save(buf, format="PNG")
        buf.seek(0)

        new_page = result_doc.new_page(width=1200, height=842)
        new_page.insert_image(new_page.rect, stream=buf.read())
        new_page.insert_text(
            fitz.Point(10, 820),
            f"Page {i+1} — Left: File 1 | Right: File 2",
            fontsize=8,
            color=(0.3, 0.3, 0.3),
        )

    doc1.close()
    doc2.close()
    result_doc.save(str(out), garbage=3, deflate=True)
    result_doc.close()

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"pages_compared": pages},
        "preview_file": render_preview(job, out_rel),
    }
