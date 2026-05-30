"""QR code generator."""
import qrcode

from features.tools.models import ToolJob
from features.tools.services import file_handler


def run(job: ToolJob) -> dict:
    text = job.options.get("text", "").strip()
    if not text:
        from features.tools.services.exceptions import ToolError

        raise ToolError("Text or URL is required.")

    qr_type = job.options.get("qr_type", "url")
    if qr_type == "upi" and not text.startswith("upi://"):
        text = f"upi://pay?pa={text}"
    elif qr_type == "whatsapp" and not text.startswith("https://"):
        text = f"https://wa.me/{text.replace('+', '')}"

    fill = job.options.get("fill_color", "black")
    back = job.options.get("back_color", "white")
    size = int(job.options.get("size", 10))

    qr = qrcode.QRCode(version=1, box_size=size, border=2)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill, back_color=back)

    out = file_handler.output_path(job, "qrcode.png")
    img.save(out)

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"qr_type": qr_type},
        "preview_file": out_rel,
    }
