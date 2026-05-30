"""Word to PDF via LibreOffice or text fallback."""
import shutil
import subprocess
import tempfile
from pathlib import Path

import fitz

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.pdf_utils import render_preview


def _find_soffice():
    candidates = (
        "soffice",
        "libreoffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    )
    for cmd in candidates:
        if cmd.startswith("/"):
            if Path(cmd).exists():
                return cmd
        else:
            found = shutil.which(cmd)
            if found:
                return found
    return None


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    out = file_handler.output_path(job, "converted.pdf")
    soffice = _find_soffice()

    if soffice:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    soffice,
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    tmp,
                    str(src),
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                raise ToolError("Conversion failed. Install LibreOffice for best results.")
            pdfs = list(Path(tmp).glob("*.pdf"))
            if not pdfs:
                raise ToolError("No PDF output from LibreOffice.")
            shutil.copy(pdfs[0], out)
    else:
        try:
            from docx import Document
        except ImportError as exc:
            raise ToolError(
                "LibreOffice not found. Install LibreOffice for Word conversion."
            ) from exc

        document = Document(str(src))
        text = "\n".join(p.text for p in document.paragraphs if p.text.strip())
        pdf = fitz.open()
        page = pdf.new_page()
        page.insert_text((50, 50), text[:8000] or "(empty document)", fontsize=11)
        pdf.save(str(out))
        pdf.close()

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"converter": "libreoffice" if soffice else "fallback"},
        "preview_file": render_preview(job, out_rel),
    }
