"""Compress images — 90% target, lossless, or balanced modes."""
import shutil
import tempfile
from pathlib import Path

from PIL import Image

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.pdf_utils import compression_stats
from features.tools.services.progress import set_progress

MAX_MEGAPIXELS = 40
TARGET_SAVED_PCT = 90  # aim for ~90% smaller file

LOSSY_PROFILES = {
    "balanced": {"jpeg_quality": 78, "webp_quality": 78, "max_dim": 2400},
    "maximum": {"jpeg_quality": 45, "webp_quality": 45, "max_dim": 1600},
}


def _strip_metadata(img: Image.Image) -> Image.Image:
    out = img.copy()
    keep = ("transparency",)
    out.info = {k: v for k, v in out.info.items() if k in keep}
    return out


def _check_size(img: Image.Image) -> None:
    w, h = img.size
    if w * h > MAX_MEGAPIXELS * 1_000_000:
        raise ToolError(
            f"Image too large ({w}×{h}). Maximum is {MAX_MEGAPIXELS} megapixels."
        )


def _to_webp_ready(img: Image.Image) -> Image.Image:
    img = _strip_metadata(img)
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        return img.convert("RGBA")
    if img.mode != "RGB":
        return img.convert("RGB")
    return img


def _resize(img: Image.Image, max_dim: int) -> Image.Image:
    w, h = img.size
    longest = max(w, h)
    if longest <= max_dim:
        return img
    scale = max_dim / longest
    return img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)


def _encode_lossy(img: Image.Image, path: Path, fmt: str, quality: int) -> None:
    if fmt == "webp":
        img.save(path, format="WEBP", quality=quality, method=4)
    else:
        rgb = img.convert("RGB") if img.mode != "RGB" else img
        rgb.save(
            path,
            format="JPEG",
            quality=quality,
            optimize=True,
            progressive=True,
            subsampling=2,
        )


def _save_png_lossless(img: Image.Image, out: Path) -> None:
    img = _strip_metadata(img)
    if img.mode == "CMYK":
        img = img.convert("RGB")
    elif img.mode not in ("RGB", "RGBA", "P", "L", "1", "LA"):
        img = img.convert("RGB")
    img.save(out, format="PNG", optimize=True, compress_level=9)


def _save_jpeg_optimize(img: Image.Image, out: Path, quality: int = 92) -> None:
    img = _to_webp_ready(img)
    if img.mode == "RGBA":
        img = img.convert("RGB")
    img.save(
        out,
        format="JPEG",
        quality=quality,
        subsampling=0,
        optimize=True,
        progressive=True,
    )


def _compress_target90(src: Path, job: ToolJob) -> tuple[Path, dict]:
    """Aggressive lossy compression targeting ~90% file size reduction."""
    orig_size = src.stat().st_size
    target_bytes = int(orig_size * (1 - TARGET_SAVED_PCT / 100))
    extra: dict = {"target_pct": TARGET_SAVED_PCT}

    img = Image.open(src)
    try:
        _check_size(img)
        base = _to_webp_ready(img)
    finally:
        img.close()

    dim_steps = [2400, 1920, 1440, 1080, 800, 640, 480]
    quality_steps = [42, 32, 26, 20, 15, 12]
    formats = ("webp", "jpeg")

    best: tuple[int, Path, str] | None = None
    hit_target: tuple[int, Path, str] | None = None
    step_i = 0
    total_steps = len(dim_steps) * len(quality_steps) * len(formats)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        for max_dim in dim_steps:
            resized = _resize(base, max_dim)
            for fmt in formats:
                suffix = ".webp" if fmt == "webp" else ".jpg"
                for quality in quality_steps:
                    step_i += 1
                    if step_i % 4 == 0:
                        set_progress(
                            job,
                            20 + int(65 * step_i / total_steps),
                            f"Compressing ({step_i}/{total_steps})…",
                        )
                    path = tmp_path / f"{max_dim}_{fmt}_{quality}{suffix}"
                    try:
                        _encode_lossy(resized, path, fmt, quality)
                    except Exception:
                        continue
                    if not path.exists():
                        continue
                    size = path.stat().st_size
                    saved = round((1 - size / orig_size) * 100) if orig_size else 0

                    if best is None or size < best[0]:
                        best = (size, path, suffix)

                    if saved >= TARGET_SAVED_PCT - 2 or size <= target_bytes:
                        hit_target = (size, path, suffix)
                        break
                if hit_target:
                    break
            if hit_target:
                break

        if not best:
            raise ToolError("Could not compress this image.")

        use = hit_target or best
        size, tmp_file, suffix = use
        out = file_handler.output_path(job, f"compressed{suffix}")
        shutil.copy2(tmp_file, out)

        saved_pct = round((1 - size / orig_size) * 100) if orig_size else 0
        extra["format_used"] = suffix
        extra["achieved_target"] = saved_pct >= TARGET_SAVED_PCT - 5

        if saved_pct >= TARGET_SAVED_PCT - 5:
            extra["message"] = f"Reached ~{saved_pct}% reduction (target {TARGET_SAVED_PCT}%)."
        else:
            extra["message"] = (
                f"Best result: {saved_pct}% smaller. "
                f"This image may not reach {TARGET_SAVED_PCT}% without heavy blur — "
                "try a smaller source or lower resolution."
            )

    return out, extra


def _pick_smallest_lossless(
    src: Path, ext: str, output_format: str, job: ToolJob
) -> tuple[Path, dict]:
    orig_size = src.stat().st_size
    extra: dict = {}

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        candidates: list[tuple[int, Path, str]] = []

        def add_variant(suffix: str, save_fn) -> None:
            path = tmp_path / f"try{suffix}"
            im = Image.open(src)
            try:
                save_fn(im, path)
            finally:
                im.close()
            if path.exists() and path.stat().st_size > 0:
                candidates.append((path.stat().st_size, path, suffix))

        if ext in (".jpg", ".jpeg"):
            add_variant(".jpg", lambda im, p: _save_jpeg_optimize(im, p, 92))
            add_variant(".jpg", lambda im, p: _save_jpeg_optimize(im, p, 85))
        elif ext == ".png":
            add_variant(".png", _save_png_lossless)
            if output_format in ("webp", "auto"):
                add_variant(".webp", lambda im, p: _save_webp_lossless(im, p))
        elif ext == ".webp":
            add_variant(".webp", lambda im, p: _save_webp_lossless(im, p))
        else:
            add_variant(ext, _save_png_lossless)

        if not candidates:
            raise ToolError("Could not compress this image.")

        candidates.sort(key=lambda x: x[0])
        best_size, best_tmp, best_suffix = candidates[0]

        if best_size >= orig_size:
            out = file_handler.output_path(job, f"compressed{ext}")
            shutil.copy2(src, out)
            extra["kept_original"] = True
            extra["message"] = "Already optimally compressed — returned your original file."
        else:
            extra["format_used"] = best_suffix
            out = file_handler.output_path(job, f"compressed{best_suffix}")
            shutil.copy2(best_tmp, out)

    return out, extra


def _save_webp_lossless(img: Image.Image, out: Path) -> None:
    img = _to_webp_ready(img)
    img.save(out, format="WEBP", lossless=True, quality=100, method=4)


def _save_lossy(img: Image.Image, out: Path, ext: str, mode: str) -> Path:
    profile = LOSSY_PROFILES.get(mode, LOSSY_PROFILES["balanced"])
    img = _to_webp_ready(img)
    img = _resize(img, profile.get("max_dim") or 99999)

    if ext in (".jpg", ".jpeg"):
        _encode_lossy(img, out, "jpeg", profile["jpeg_quality"])
        return out
    elif ext == ".png":
        if mode == "maximum" and img.mode not in ("RGBA", "LA"):
            jpg_out = out.with_suffix(".jpg")
            _encode_lossy(img, jpg_out, "jpeg", profile["jpeg_quality"])
            return jpg_out
        else:
            _save_png_lossless(img, out)
            return out
    elif ext == ".webp":
        _encode_lossy(img, out, "webp", profile["webp_quality"])
        return out
    else:
        _encode_lossy(img, out, "webp", profile["webp_quality"])
        return out


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    mode = job.options.get("mode", "target90")
    output_format = job.options.get("output_format", "auto")

    set_progress(job, 10, "Loading image…")
    ext = src.suffix.lower()

    if mode == "target90":
        set_progress(job, 18, f"Targeting {TARGET_SAVED_PCT}% smaller…")
        out, extra = _compress_target90(src, job)
    elif mode == "lossless":
        set_progress(job, 40, "Lossless optimization…")
        out, extra = _pick_smallest_lossless(src, ext, output_format, job)
    else:
        img = Image.open(src)
        try:
            _check_size(img)
            set_progress(job, 50, "Compressing…")
            out = file_handler.output_path(job, f"compressed{ext}")
            out = _save_lossy(img, out, ext, mode)
            extra = {}
        finally:
            img.close()

    set_progress(job, 95, "Done…")
    out_rel = file_handler.to_relative(out)
    stats = compression_stats(src_rel, out_rel)
    stats["mode"] = mode
    stats["lossless"] = mode == "lossless"
    stats.update(extra)

    return {
        "output_file": out_rel,
        "compression_stat": stats,
        "preview_file": out_rel,
    }
