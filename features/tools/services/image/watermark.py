"""Add text watermark to an image."""
from PIL import Image, ImageDraw, ImageFont

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    opts = job.options or {}
    text = opts.get("text", "SD-Toolx")
    opacity = int(float(opts.get("opacity", 0.5)) * 255)
    position = opts.get("position", "center")

    try:
        img = Image.open(str(src)).convert("RGBA")
    except Exception as exc:
        raise ToolError(f"Cannot open image: {exc}") from exc

    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    fontsize = max(16, w // 10)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", fontsize)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    positions = {
        "center": ((w - tw) // 2, (h - th) // 2),
        "top-left": (10, 10),
        "top-right": (w - tw - 10, 10),
        "bottom-left": (10, h - th - 10),
        "bottom-right": (w - tw - 10, h - th - 10),
    }
    x, y = positions.get(position, positions["center"])
    draw.text((x, y), text, font=font, fill=(255, 255, 255, opacity))

    result = Image.alpha_composite(img, overlay).convert("RGB")
    out = file_handler.output_path(job, f"watermarked{src.suffix.lower()}")
    result.save(str(out))

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"text": text, "position": position},
        "preview_file": out_rel,
    }
