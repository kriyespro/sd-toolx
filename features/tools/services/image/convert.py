"""Convert image format (JPG ↔ PNG ↔ WebP ↔ BMP)."""
from PIL import Image

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError

FORMAT_MAP = {
    "jpg": ("JPEG", ".jpg"),
    "jpeg": ("JPEG", ".jpg"),
    "png": ("PNG", ".png"),
    "webp": ("WEBP", ".webp"),
    "bmp": ("BMP", ".bmp"),
    "gif": ("GIF", ".gif"),
}


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    target = (job.options.get("to_format", "png") or "png").lower().strip(".")

    pil_fmt, ext = FORMAT_MAP.get(target, ("PNG", ".png"))
    out = file_handler.output_path(job, f"converted{ext}")

    try:
        img = Image.open(str(src))
    except Exception as exc:
        raise ToolError(f"Cannot open image: {exc}") from exc

    if pil_fmt == "JPEG" and img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGB")
    elif pil_fmt == "GIF" and img.mode not in ("P", "L"):
        img = img.convert("P", palette=Image.ADAPTIVE)

    img.save(str(out), format=pil_fmt)
    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"from": src.suffix.lstrip(".").upper(), "to": pil_fmt},
        "preview_file": out_rel,
    }
