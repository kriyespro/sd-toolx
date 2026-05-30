"""Add signature to PDF."""
import base64
import io

import fitz
from PIL import Image

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.pdf_utils import render_preview


def run(job: ToolJob) -> dict:
    if len(job.input_files) < 1:
        raise ToolError("PDF file required.")

    pdf_rel = job.input_files[0]
    pdf_path = file_handler.to_absolute(pdf_rel)
    doc = fitz.open(pdf_path)

    page_num = int(job.options.get("page", 1)) - 1
    if page_num < 0 or page_num >= doc.page_count:
        page_num = 0
    page = doc[page_num]

    sig_data = job.options.get("signature_data", "")
    sig_rel = job.input_files[1] if len(job.input_files) > 1 else None

    if sig_data.startswith("data:image"):
        if "," not in sig_data:
            doc.close()
            raise ToolError("Invalid signature data format.")
        _, b64 = sig_data.split(",", 1)
        img_bytes = base64.b64decode(b64)
        img = Image.open(io.BytesIO(img_bytes))
    elif sig_rel:
        img = Image.open(file_handler.to_absolute(sig_rel))
    else:
        doc.close()
        raise ToolError("Signature image required.")

    if img.mode != "RGBA":
        img = img.convert("RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    rect = page.rect
    w = float(job.options.get("width", 120))
    h = float(job.options.get("height", 50))
    x = float(job.options.get("x", rect.width - w - 50))
    y = float(job.options.get("y", rect.height - h - 50))
    sig_rect = fitz.Rect(x, y, x + w, y + h)
    page.insert_image(sig_rect, stream=buf.read())

    out = file_handler.output_path(job, "signed.pdf")
    doc.save(str(out))
    doc.close()

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"signed": True},
        "preview_file": render_preview(job, out_rel),
    }
