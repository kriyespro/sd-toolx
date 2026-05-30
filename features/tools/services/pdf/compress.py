"""Compress PDF — Ghostscript or safe per-image recompression."""
import io
import logging
import shutil
import subprocess
from pathlib import Path

import fitz
from PIL import Image

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.pdf_utils import compression_stats, render_preview
from features.tools.services.progress import set_progress

logger = logging.getLogger(__name__)

GS_SETTINGS = {
    "low": "/screen",
    "medium": "/ebook",
    "high": "/printer",
}

QUALITY_PROFILES = {
    "low": {"jpeg_quality": 25, "max_dim": 900},
    "medium": {"jpeg_quality": 48, "max_dim": 1400},
    "high": {"jpeg_quality": 68, "max_dim": 2200},
}


def _find_ghostscript():
    for cmd in (
        "gs",
        "gswin64c",
        "gswin32c",
        "/usr/local/bin/gs",
        "/opt/homebrew/bin/gs",
    ):
        path = shutil.which(cmd) if not cmd.startswith("/") else cmd
        if path and Path(path).exists():
            return path
    return None


def _compress_ghostscript(src: Path, out: Path, quality: str) -> bool:
    gs = _find_ghostscript()
    if not gs:
        return False
    setting = GS_SETTINGS.get(quality, "/ebook")
    try:
        subprocess.run(
            [
                gs,
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                f"-dPDFSETTINGS={setting}",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                f"-sOutputFile={out}",
                str(src),
            ],
            check=True,
            capture_output=True,
            timeout=180,
        )
        return out.exists() and out.stat().st_size > 0
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        logger.warning("Ghostscript compress failed: %s", exc)
        return False


def _pil_to_jpeg_bytes(data: bytes, ext: str, jpeg_quality: int, max_dim: int) -> bytes | None:
    try:
        img = Image.open(io.BytesIO(data))
    except Exception:
        return None

    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGB")
    elif img.mode == "CMYK":
        img = img.convert("RGB")
    elif img.mode != "RGB":
        img = img.convert("RGB")

    w, h = img.size
    longest = max(w, h)
    if longest > max_dim:
        scale = max_dim / longest
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=jpeg_quality, optimize=True)
    return buf.getvalue()


def _compress_images_safe(
    doc: fitz.Document, profile: dict, job: ToolJob | None = None
) -> int:
    jpeg_quality = profile["jpeg_quality"]
    max_dim = profile["max_dim"]
    updated = 0
    seen: set[int] = set()
    xrefs: list[tuple] = []

    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            if xref not in seen:
                seen.add(xref)
                xrefs.append((page, xref))

    total = len(xrefs) or 1
    for i, (page, xref) in enumerate(xrefs):
        if job:
            set_progress(
                job,
                18 + int(65 * (i + 1) / total),
                f"Compressing image {i + 1} of {total}…",
            )
        try:
            info = doc.extract_image(xref)
        except Exception:
            continue
        raw = info.get("image")
        if not raw or len(raw) < 500:
            continue
        new_bytes = _pil_to_jpeg_bytes(
            raw, info.get("ext", "jpeg"), jpeg_quality, max_dim
        )
        if not new_bytes:
            continue
        try:
            page.replace_image(xref, stream=new_bytes)
            updated += 1
        except Exception as exc:
            logger.debug("replace_image xref %s: %s", xref, exc)
    return updated


def _compress_pymupdf(
    src: Path, out: Path, quality: str, job: ToolJob | None = None
) -> str:
    if job:
        set_progress(job, 15, "Opening PDF…")
    profile = QUALITY_PROFILES.get(quality, QUALITY_PROFILES["medium"])
    doc = fitz.open(src)
    try:
        doc.rewrite_images(
            dpi=max(72, profile["max_dim"] // 8),
            quality=profile["jpeg_quality"],
        )
    except Exception as exc:
        logger.debug("rewrite_images: %s", exc)

    n = _compress_images_safe(doc, profile, job)
    if job:
        set_progress(job, 88, "Writing compressed PDF…")
    doc.save(
        str(out),
        garbage=4,
        deflate=True,
        deflate_images=True,
        deflate_fonts=True,
        clean=True,
    )
    doc.close()
    return "pymupdf-images" if n else "pymupdf"


def _saved_pct(src: Path, out: Path) -> float:
    if not src.exists() or not out.exists():
        return 0.0
    orig = src.stat().st_size
    if orig == 0:
        return 0.0
    return max(0.0, round((1 - out.stat().st_size / orig) * 100, 1))


def _output_is_blank(out: Path) -> bool:
    try:
        doc = fitz.open(out)
        if doc.page_count == 0:
            doc.close()
            return True
        pix = doc[0].get_pixmap(alpha=False)
        doc.close()
        if not pix.samples:
            return True
        sample = pix.samples[: min(5000, len(pix.samples))]
        return sum(sample) / len(sample) < 15
    except Exception:
        return False


def compress_path(
    src: Path, out: Path, quality: str = "medium", job: ToolJob | None = None
) -> dict:
    if not src.exists():
        raise ToolError("Source file not found.")

    if job:
        set_progress(job, 20, "Compressing…")

    engine = "pymupdf"
    if _compress_ghostscript(src, out, quality):
        engine = "ghostscript"
        if job:
            set_progress(job, 85, "Ghostscript finished…")
    else:
        engine = _compress_pymupdf(src, out, quality, job)

    if not out.exists() or out.stat().st_size == 0:
        raise ToolError("Compression failed. Try a different quality setting.")

    if _output_is_blank(out):
        raise ToolError(
            "Compression produced an invalid file. Try Balanced or High quality."
        )

    orig = src.stat().st_size
    new = out.stat().st_size
    pct = _saved_pct(src, out)
    stats = {
        "original_bytes": orig,
        "output_bytes": new,
        "saved_pct": int(pct) if pct == int(pct) else pct,
        "engine": engine,
    }
    if stats["saved_pct"] < 3:
        stats["message"] = "Limited savings — file may already be optimized."
    return stats


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    quality = job.options.get("quality", "medium")
    out = file_handler.output_path(job, "compressed.pdf")

    stats = compress_path(src, out, quality, job)
    out_rel = file_handler.to_relative(out)
    preview = render_preview(job, out_rel)

    return {
        "output_file": out_rel,
        "compression_stat": stats,
        "preview_file": preview,
    }
