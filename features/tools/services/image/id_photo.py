"""Passport / ID photo generator — resize + background color."""
from PIL import Image, ImageOps

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError

PRESETS = {
    "passport_india": (413, 531),
    "aadhaar": (413, 531),
    "pan": (413, 531),
    "visa_us": (600, 600),
    "visa_uk": (354, 472),
    "linkedin": (400, 400),
    "2x2": (600, 600),
}


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    opts = job.options or {}

    preset = opts.get("preset", "passport_india")
    bg_color = opts.get("bg_color", "white")
    size = PRESETS.get(preset, (413, 531))

    try:
        img = Image.open(str(src)).convert("RGBA")
    except Exception as exc:
        raise ToolError(f"Cannot open image: {exc}") from exc

    img_ratio = img.width / img.height
    target_ratio = size[0] / size[1]

    if img_ratio > target_ratio:
        new_h = img.height
        new_w = int(img.height * target_ratio)
    else:
        new_w = img.width
        new_h = int(img.width / target_ratio)

    left = (img.width - new_w) // 2
    top = (img.height - new_h) // 2
    cropped = img.crop((left, top, left + new_w, top + new_h))
    resized = cropped.resize(size, Image.LANCZOS)

    bg = Image.new("RGB", size, bg_color)
    bg.paste(resized, mask=resized.split()[3] if resized.mode == "RGBA" else None)

    out = file_handler.output_path(job, f"id_photo_{preset}.jpg")
    bg.save(str(out), format="JPEG", quality=95)

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"preset": preset, "size_px": f"{size[0]}×{size[1]}"},
        "preview_file": out_rel,
    }
