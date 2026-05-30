"""Add text watermark to every page of a PDF using an image overlay."""
import io
import math

import fitz
from PIL import Image, ImageDraw, ImageFont

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.pdf_utils import render_preview


def _hex_to_rgb(color_hex: str) -> tuple[int, int, int]:
    h = color_hex.lstrip("#")
    try:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except Exception:
        return 128, 128, 128


def _make_watermark_image(text: str, width: int, height: int,
                           rotation: int, opacity: float,
                           color_rgb: tuple[int, int, int]) -> bytes:
    """Create a watermark PNG (transparent) matching the page size."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    fontsize = max(20, min(width // 6, 72))
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", fontsize)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    alpha = int(opacity * 255)
    fill = (*color_rgb, alpha)

    txt_img = Image.new("RGBA", (tw + 20, th + 20), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_img)
    txt_draw.text((10, 10), text, font=font, fill=fill)

    angle = rotation % 360
    rotated = txt_img.rotate(angle, expand=True)

    rw, rh = rotated.size
    x = (width - rw) // 2
    y = (height - rh) // 2
    img.paste(rotated, (x, y), rotated)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    opts = job.options or {}

    text = opts.get("text", "CONFIDENTIAL")
    opacity = float(opts.get("opacity", 0.3))
    rotation = int(opts.get("rotation", 45))
    color = _hex_to_rgb(opts.get("color", "#888888"))

    out = file_handler.output_path(job, "watermarked.pdf")
    doc = fitz.open(str(src))

    for page in doc:
        rect = page.rect
        w, h = int(rect.width * 2), int(rect.height * 2)
        wm_bytes = _make_watermark_image(text, w, h, rotation, opacity, color)
        page.insert_image(rect, stream=wm_bytes, overlay=True)

    doc.save(str(out), garbage=3, deflate=True)
    doc.close()

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"text": text, "opacity": opacity},
        "preview_file": render_preview(job, out_rel),
    }
