"""Remove image background — uses rembg if available, Pillow chroma-key fallback."""
from io import BytesIO

from PIL import Image

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.progress import set_progress


def _remove_bg_rembg(input_data: bytes) -> bytes:
    from rembg import remove
    return remove(input_data)


def _remove_bg_pillow(img: Image.Image) -> Image.Image:
    """Simple flood-fill from corners to detect background color and make it transparent."""
    img = img.convert("RGBA")
    data = img.load()
    w, h = img.size

    # Sample corners to estimate background color
    corners = [data[0, 0], data[w - 1, 0], data[0, h - 1], data[w - 1, h - 1]]
    avg_r = sum(c[0] for c in corners) // 4
    avg_g = sum(c[1] for c in corners) // 4
    avg_b = sum(c[2] for c in corners) // 4
    tolerance = 40

    # Make pixels close to background color transparent
    for y in range(h):
        for x in range(w):
            r, g, b, a = data[x, y]
            if (abs(r - avg_r) < tolerance and
                    abs(g - avg_g) < tolerance and
                    abs(b - avg_b) < tolerance):
                data[x, y] = (r, g, b, 0)

    return img


def run(job: ToolJob) -> dict:
    set_progress(job, 20, "Loading image…")
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)

    with open(src, "rb") as f:
        input_data = f.read()

    try:
        set_progress(job, 40, "Removing background (AI)…")
        output_data = _remove_bg_rembg(input_data)
        out = file_handler.output_path(job, "no-background.png")
        img = Image.open(BytesIO(output_data))
        img.save(str(out), format="PNG", optimize=True)
        engine = "rembg"
    except (ImportError, Exception):
        set_progress(job, 40, "Removing background…")
        img = Image.open(BytesIO(input_data))
        result = _remove_bg_pillow(img)
        out = file_handler.output_path(job, "no-background.png")
        result.save(str(out), format="PNG", optimize=True)
        engine = "pillow-chroma"

    set_progress(job, 90, "Saving PNG…")
    out_rel = file_handler.to_relative(out)
    orig = src.stat().st_size
    new = out.stat().st_size

    return {
        "output_file": out_rel,
        "compression_stat": {
            "original_bytes": orig,
            "output_bytes": new,
            "engine": engine,
            "note": "For best results, install rembg on the server." if engine != "rembg" else "",
        },
        "preview_file": out_rel,
    }
