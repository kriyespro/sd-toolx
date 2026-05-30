"""Remove password from PDF."""
import fitz

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.pdf_utils import render_preview


def run(job: ToolJob) -> dict:
    password = job.options.get("password", "").strip()
    if not password:
        raise ToolError("Enter the PDF password to unlock.")

    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)

    try:
        doc = fitz.open(src)
        if doc.needs_pass and not doc.authenticate(password):
            doc.close()
            raise ToolError("Incorrect password.")
        if doc.is_encrypted and not doc.authenticate(password):
            doc.close()
            raise ToolError("Incorrect password.")
    except ToolError:
        raise
    except Exception as exc:
        raise ToolError("Could not open PDF. Check the password.") from exc

    out = file_handler.output_path(job, "unlocked.pdf")
    doc.save(str(out), encryption=fitz.PDF_ENCRYPT_NONE)
    doc.close()

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"unlocked": True},
        "preview_file": render_preview(job, out_rel),
    }
