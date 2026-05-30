"""Images to PDF."""
import fitz
from PIL import Image

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.pdf_utils import render_preview


def run(job: ToolJob) -> dict:
    page_size = job.options.get("page_size", "a4")
    sizes = {
        "a4": fitz.paper_rect("a4"),
        "letter": fitz.paper_rect("letter"),
        "fit": None,
    }
    rect = sizes.get(page_size)

    pdf = fitz.open()
    order = job.options.get("order", list(range(len(job.input_files))))

    temps = []
    for idx in order:
        if idx >= len(job.input_files):
            continue
        img_path = file_handler.to_absolute(job.input_files[idx])
        img = Image.open(img_path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        temp = file_handler.job_root(job.id) / f"tmp_{idx}.jpg"
        img.save(temp, "JPEG", quality=90)
        temps.append(temp)

        if page_size == "fit":
            page = pdf.new_page(width=img.width, height=img.height)
        else:
            page_rect = rect or fitz.paper_rect("a4")
            page = pdf.new_page(width=page_rect.width, height=page_rect.height)
        page.insert_image(page.rect, filename=str(temp))

    out = file_handler.output_path(job, "images.pdf")
    pdf.save(str(out))
    pdf.close()
    for temp in temps:
        temp.unlink(missing_ok=True)

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"images": len(job.input_files)},
        "preview_file": render_preview(job, out_rel),
    }
