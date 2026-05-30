"""Map tool slugs to processing functions."""
from features.tools.models import ToolJob
from features.tools.services.image import compress as compress_image
from features.tools.services.image import remove_bg
from features.tools.services.image import to_pdf as img_to_pdf
from features.tools.services.image import convert as convert_image
from features.tools.services.image import id_photo
from features.tools.services.image import resize as resize_image
from features.tools.services.image import upscale as upscale_image
from features.tools.services.image import watermark as watermark_image
from features.tools.services.office import word_to_pdf
from features.tools.services.office import excel_to_pdf
from features.tools.services.office import ppt_to_pdf
from features.tools.services.pdf import (
    ai_extract,
    ai_grammar,
    ai_translate,
    compare,
    compress,
    fill_form,
    merge,
    ocr,
    protect,
    redact,
    reorder,
    repair,
    rotate,
    sign,
    split,
    summarize,
    to_excel,
    to_jpg,
    to_ppt,
    to_word,
    unlock,
    watermark,
)
from features.tools.services import barcode, qr, url_shortener, word_counter


HANDLERS = {
    "compress-pdf": compress.run,
    "merge-pdf": merge.run,
    "split-pdf": split.run,
    "rotate-pdf": rotate.run,
    "pdf-to-jpg": to_jpg.run,
    "img-to-pdf": img_to_pdf.run,
    "word-to-pdf": word_to_pdf.run,
    "excel-to-pdf": excel_to_pdf.run,
    "ppt-to-pdf": ppt_to_pdf.run,
    "compress-image": compress_image.run,
    "sign-pdf": sign.run,
    "qr-generator": qr.run,
    "pdf-to-word": to_word.run,
    "pdf-to-excel": to_excel.run,
    "pdf-to-ppt": to_ppt.run,
    "protect-pdf": protect.run,
    "reorder-pdf": reorder.run,
    "delete-pdf-pages": reorder.run,
    "unlock-pdf": unlock.run,
    "watermark-pdf": watermark.run,
    "repair-pdf": repair.run,
    "redact-pdf": redact.run,
    "compare-pdf": compare.run,
    "fill-pdf-form": fill_form.run,
    "ocr": ocr.run,
    "ai-translate-pdf": ai_translate.run,
    "ai-extract-data": ai_extract.run,
    "remove-background": remove_bg.run,
    "ai-summarize-pdf": summarize.run,
    "upscale-image": upscale_image.run,
    "word-counter": word_counter.run,
    "resize-image": resize_image.run,
    "convert-image": convert_image.run,
    "watermark-image": watermark_image.run,
    "id-photo": id_photo.run,
    "ai-grammar-check": ai_grammar.run,
    "barcode-generator": barcode.run,
    "url-shortener": url_shortener.run,
}


def run_handler(job: ToolJob, request=None) -> dict:
    handler = HANDLERS.get(job.tool_slug)
    if not handler:
        raise ValueError(f"No handler for {job.tool_slug}")
    return handler(job)
