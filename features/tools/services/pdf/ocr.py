"""OCR: extract text from scanned PDF or image."""
import io
import shutil
import subprocess
import tempfile
from pathlib import Path

import fitz
from PIL import Image

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError


def _tesseract_available():
    return shutil.which("tesseract") is not None


def _ocr_image_bytes(img_bytes: bytes, lang: str = "eng") -> str:
    with tempfile.TemporaryDirectory() as tmp:
        img_path = Path(tmp) / "page.png"
        img_path.write_bytes(img_bytes)
        out_base = Path(tmp) / "out"
        result = subprocess.run(
            ["tesseract", str(img_path), str(out_base), "-l", lang],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            return ""
        txt_file = Path(str(out_base) + ".txt")
        return txt_file.read_text(encoding="utf-8", errors="replace") if txt_file.exists() else ""


def _extract_text_fitz(src: Path) -> str:
    doc = fitz.open(str(src))
    parts = []
    for page in doc:
        parts.append(page.get_text())
    doc.close()
    return "\n\n".join(parts)


def _ocr_pdf_with_tesseract(src: Path, lang: str) -> str:
    """Render PDF pages to images via PyMuPDF and OCR each with tesseract."""
    doc = fitz.open(str(src))
    all_text = []
    for i, page in enumerate(doc):
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_bytes = pix.tobytes("png")
        text = _ocr_image_bytes(img_bytes, lang)
        all_text.append(text or page.get_text())
    doc.close()
    return "\n\n".join(all_text)


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    lang = job.options.get("lang", "eng")
    out = file_handler.output_path(job, "ocr_output.txt")

    ext = src.suffix.lower()
    is_pdf = ext == ".pdf"

    if _tesseract_available():
        if is_pdf:
            text = _ocr_pdf_with_tesseract(src, lang)
        else:
            img = Image.open(str(src))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            text = _ocr_image_bytes(buf.getvalue(), lang)
    else:
        if is_pdf:
            text = _extract_text_fitz(src)
        else:
            text = "(OCR requires Tesseract. For images, install tesseract on the server.)"

    if not text.strip():
        text = "(No text could be extracted from this file.)"

    out.write_text(text, encoding="utf-8")
    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {
            "chars": len(text),
            "engine": "tesseract" if _tesseract_available() else "fitz-text",
        },
        "preview_file": "",
    }
