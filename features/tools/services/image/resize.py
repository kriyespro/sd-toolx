"""Resize image by pixels or percentage."""
from PIL import Image

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    opts = job.options or {}

    mode = opts.get("mode", "pixels")
    lock_ratio = opts.get("lock_ratio", "true") == "true"

    try:
        img = Image.open(str(src))
    except Exception as exc:
        raise ToolError(f"Cannot open image: {exc}") from exc

    orig_w, orig_h = img.size
    fmt = img.format or "PNG"

    if mode == "percent":
        pct = max(1, min(500, int(opts.get("percent", 50)))) / 100
        new_w = max(1, int(orig_w * pct))
        new_h = max(1, int(orig_h * pct))
    else:
        new_w = int(opts.get("width") or orig_w)
        new_h = int(opts.get("height") or orig_h)
        if lock_ratio and (new_w != orig_w or new_h != orig_h):
            ratio = orig_w / orig_h
            if new_w / new_h > ratio:
                new_w = int(new_h * ratio)
            else:
                new_h = int(new_w / ratio)

    new_w = max(1, min(new_w, 8000))
    new_h = max(1, min(new_h, 8000))
    resized = img.resize((new_w, new_h), Image.LANCZOS)

    out_name = f"resized_{new_w}x{new_h}{src.suffix.lower()}"
    out = file_handler.output_path(job, out_name)
    if fmt == "JPEG" and resized.mode in ("RGBA", "P"):
        resized = resized.convert("RGB")
    resized.save(str(out))

    return {
        "output_file": file_handler.to_relative(out),
        "compression_stat": {
            "original": f"{orig_w}×{orig_h}",
            "output": f"{new_w}×{new_h}",
        },
        "preview_file": file_handler.to_relative(out),
    }
