"""Add password protection to PDF."""
import fitz

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.pdf_utils import render_preview


def run(job: ToolJob) -> dict:
    password = job.options.get("password", "").strip()
    if not password:
        raise ToolError("Please enter a password.")

    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    doc = fitz.open(src)
    out = file_handler.output_path(job, "protected.pdf")
    doc.save(str(out), encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw=password, user_pw=password)
    doc.close()

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"protected": True},
        "preview_file": "",
    }
