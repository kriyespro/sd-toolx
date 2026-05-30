"""Upscale image 2x using Pillow (high-quality Lanczos resampling)."""
from pathlib import Path

from PIL import Image

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    scale = int(job.options.get("scale", 2))
    if scale not in (2, 4):
        scale = 2

    out_name = f"upscaled_{scale}x{src.suffix.lower()}"
    out = file_handler.output_path(job, out_name)

    try:
        img = Image.open(str(src))
    except Exception as exc:
        raise ToolError(f"Cannot open image: {exc}") from exc

    if img.mode == "P":
        img = img.convert("RGBA")

    new_w = img.width * scale
    new_h = img.height * scale
    if new_w > 8000 or new_h > 8000:
        raise ToolError("Input too large. Max output is 8000×8000px.")

    upscaled = img.resize((new_w, new_h), Image.LANCZOS)
    fmt = img.format or "PNG"
    if fmt == "JPEG" and upscaled.mode in ("RGBA", "P"):
        upscaled = upscaled.convert("RGB")
    upscaled.save(str(out))

    orig_size = file_handler.file_size(file_handler.to_relative(src))
    new_size = file_handler.file_size(file_handler.to_relative(out))
    return {
        "output_file": file_handler.to_relative(out),
        "compression_stat": {
            "original_pixels": f"{img.width}×{img.height}",
            "output_pixels": f"{new_w}×{new_h}",
            "scale": f"{scale}x",
            "original_bytes": orig_size,
            "output_bytes": new_size,
        },
        "preview_file": file_handler.to_relative(out),
    }
