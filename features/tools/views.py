from django.shortcuts import render

from features.tools.registry import TOOLS, live_tools
from features.tools.views_base import ToolPageView, job_download, job_status, recent_files_partial


def tools_index(request):
    return render(request, "pages/tools/index.jinja", {"tools": live_tools()})


class CompressPdfView(ToolPageView):
    tool_slug = "compress-pdf"


class MergePdfView(ToolPageView):
    tool_slug = "merge-pdf"

    def build_options(self, request, tool):
        order = request.POST.get("order", "")
        if order:
            return {"order": [int(x) for x in order.split(",") if x.strip().isdigit()]}
        uploads = self.get_uploads(request, tool)
        return {"order": list(range(len(uploads)))}


class SplitPdfView(ToolPageView):
    tool_slug = "split-pdf"


class RotatePdfView(ToolPageView):
    tool_slug = "rotate-pdf"


class PdfToJpgView(ToolPageView):
    tool_slug = "pdf-to-jpg"


class ImgToPdfView(ToolPageView):
    tool_slug = "img-to-pdf"

    def build_options(self, request, tool):
        uploads = self.get_uploads(request, tool)
        return {
            "page_size": request.POST.get("page_size", "a4"),
            "order": list(range(len(uploads))),
        }


class WordToPdfView(ToolPageView):
    tool_slug = "word-to-pdf"


class CompressImageView(ToolPageView):
    tool_slug = "compress-image"


class SignPdfView(ToolPageView):
    tool_slug = "sign-pdf"

    def build_options(self, request, tool):
        return {
            "signature_data": request.POST.get("signature_data", ""),
            "page": request.POST.get("page", "1"),
            "x": request.POST.get("x", "50"),
            "y": request.POST.get("y", "50"),
            "width": request.POST.get("width", "120"),
            "height": request.POST.get("height", "50"),
        }


class PdfToWordView(ToolPageView):
    tool_slug = "pdf-to-word"


class ReorderPdfView(ToolPageView):
    tool_slug = "reorder-pdf"

    def build_options(self, request, tool):
        order = request.POST.get("order", "")
        delete_pages = request.POST.getlist("delete_pages")
        opts = {}
        if order:
            opts["order"] = [int(x) for x in order.split(",") if x.strip().isdigit()]
        if delete_pages:
            opts["delete_pages"] = delete_pages
        return opts


class DeletePdfPagesView(ToolPageView):
    tool_slug = "delete-pdf-pages"

    def build_options(self, request, tool):
        return {"delete_pages": request.POST.getlist("delete_pages")}


class UnlockPdfView(ToolPageView):
    tool_slug = "unlock-pdf"


class ProtectPdfView(ToolPageView):
    tool_slug = "protect-pdf"


class RemoveBackgroundView(ToolPageView):
    tool_slug = "remove-background"


class AiSummarizePdfView(ToolPageView):
    tool_slug = "ai-summarize-pdf"


class QrGeneratorView(ToolPageView):
    tool_slug = "qr-generator"


# ── Phase 5 views ──────────────────────────────────────────────────

class ExcelToPdfView(ToolPageView):
    tool_slug = "excel-to-pdf"


class PptToPdfView(ToolPageView):
    tool_slug = "ppt-to-pdf"


class PdfToExcelView(ToolPageView):
    tool_slug = "pdf-to-excel"


class PdfToPptView(ToolPageView):
    tool_slug = "pdf-to-ppt"


class WatermarkPdfView(ToolPageView):
    tool_slug = "watermark-pdf"

    def build_options(self, request, tool):
        return {
            "text": request.POST.get("text", "CONFIDENTIAL"),
            "opacity": request.POST.get("opacity", "0.3"),
            "rotation": request.POST.get("rotation", "45"),
            "color": request.POST.get("color", "#888888"),
        }


class RepairPdfView(ToolPageView):
    tool_slug = "repair-pdf"


class RedactPdfView(ToolPageView):
    tool_slug = "redact-pdf"

    def build_options(self, request, tool):
        return {"search_terms": request.POST.get("search_terms", "")}


class ComparePdfView(ToolPageView):
    tool_slug = "compare-pdf"


class FillPdfFormView(ToolPageView):
    tool_slug = "fill-pdf-form"

    def build_options(self, request, tool):
        import json
        field_values = {}
        for key, val in request.POST.items():
            if key.startswith("field_"):
                field_name = key[len("field_"):]
                field_values[field_name] = val
        return {"field_values": json.dumps(field_values)}


class OcrView(ToolPageView):
    tool_slug = "ocr"

    def build_options(self, request, tool):
        return {"lang": request.POST.get("lang", "eng")}


class AiTranslatePdfView(ToolPageView):
    tool_slug = "ai-translate-pdf"

    def build_options(self, request, tool):
        return {"target_lang": request.POST.get("target_lang", "hi")}


class AiExtractDataView(ToolPageView):
    tool_slug = "ai-extract-data"


class UpscaleImageView(ToolPageView):
    tool_slug = "upscale-image"

    def build_options(self, request, tool):
        return {"scale": request.POST.get("scale", "2")}


class WordCounterView(ToolPageView):
    tool_slug = "word-counter"

    def build_options(self, request, tool):
        return {"text": request.POST.get("text", "")}


# ── Phase 6 views ──────────────────────────────────────────────────

class ResizeImageView(ToolPageView):
    tool_slug = "resize-image"

    def build_options(self, request, tool):
        return {
            "mode": request.POST.get("mode", "pixels"),
            "width": request.POST.get("width", ""),
            "height": request.POST.get("height", ""),
            "percent": request.POST.get("percent", "50"),
            "lock_ratio": request.POST.get("lock_ratio", "true"),
        }


class ConvertImageView(ToolPageView):
    tool_slug = "convert-image"

    def build_options(self, request, tool):
        return {"to_format": request.POST.get("to_format", "png")}


class WatermarkImageView(ToolPageView):
    tool_slug = "watermark-image"

    def build_options(self, request, tool):
        return {
            "text": request.POST.get("text", "SD-Toolx"),
            "opacity": request.POST.get("opacity", "0.5"),
            "position": request.POST.get("position", "center"),
        }


class IdPhotoView(ToolPageView):
    tool_slug = "id-photo"

    def build_options(self, request, tool):
        return {
            "preset": request.POST.get("preset", "passport_india"),
            "bg_color": request.POST.get("bg_color", "white"),
        }


class AiGrammarCheckView(ToolPageView):
    tool_slug = "ai-grammar-check"


class BarcodeGeneratorView(ToolPageView):
    tool_slug = "barcode-generator"

    def build_options(self, request, tool):
        return {
            "text": request.POST.get("text", ""),
            "barcode_type": request.POST.get("barcode_type", "code128"),
        }


class UrlShortenerView(ToolPageView):
    tool_slug = "url-shortener"

    def build_options(self, request, tool):
        return {"url": request.POST.get("url", "")}
