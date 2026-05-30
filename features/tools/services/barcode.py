"""Barcode generator using python-barcode."""
from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError

DIGIT_REQUIREMENTS = {
    "ean13": (12, "EAN-13 requires exactly 12 digits (check digit added automatically)."),
    "ean8": (7, "EAN-8 requires exactly 7 digits (check digit added automatically)."),
    "upca": (11, "UPC-A requires exactly 11 digits (check digit added automatically)."),
    "isbn13": (12, "ISBN-13 requires exactly 12 digits."),
}


def _validate_text(text: str, barcode_type: str) -> None:
    req = DIGIT_REQUIREMENTS.get(barcode_type)
    if not req:
        return
    digits_only = text.replace("-", "").replace(" ", "")
    expected, msg = req
    if not digits_only.isdigit():
        raise ToolError(f"{barcode_type.upper()} barcodes only accept digits. {msg}")
    if len(digits_only) != expected:
        raise ToolError(
            f"{barcode_type.upper()} needs exactly {expected} digits, got {len(digits_only)}. {msg}"
        )


def run(job: ToolJob) -> dict:
    opts = job.options or {}
    text = opts.get("text", "").strip()
    barcode_type = opts.get("barcode_type", "code128").lower()

    if not text:
        raise ToolError("No text provided for barcode.")

    try:
        import barcode
        from barcode.writer import ImageWriter
    except ImportError as exc:
        raise ToolError("python-barcode not installed. Run: pip install python-barcode[images]") from exc

    type_map = {
        "code128": "code128",
        "ean13": "ean13",
        "ean8": "ean8",
        "upca": "upca",
        "isbn13": "isbn13",
        "code39": "code39",
    }
    barcode_cls_name = type_map.get(barcode_type, "code128")
    _validate_text(text, barcode_type)

    try:
        barcode_cls = barcode.get_barcode_class(barcode_cls_name)
    except Exception as exc:
        raise ToolError(f"Barcode type not supported: {barcode_type}") from exc

    out = file_handler.output_path(job, f"barcode_{barcode_type}.png")

    try:
        bc = barcode_cls(text, writer=ImageWriter())
        bc.save(str(out).replace(".png", ""))
        if not out.exists():
            out_candidates = list(out.parent.glob("barcode_*.png"))
            if out_candidates:
                out = out_candidates[0]
    except Exception as exc:
        raise ToolError(f"Cannot generate barcode: {exc}") from exc

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"type": barcode_type, "text": text},
        "preview_file": out_rel,
    }
