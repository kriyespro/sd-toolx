"""PDF page thumbnail preview for reorder/delete tools."""
import base64
import io

import fitz
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from features.tools.registry import get_tool
from features.tools.services.limits import check_can_process
from features.tools.services.exceptions import FileValidationError, UpgradeRequired
from features.tools.views_base import _render_partial


@require_POST
def page_thumbnails(request, tool_slug):
    tool = get_tool(tool_slug)
    upload = request.FILES.get("file")
    if not upload:
        return _render_partial(
            request,
            "partials/_tool_error.jinja",
            {"tool": tool, "message": "Please select a PDF first."},
        )
    try:
        limits = check_can_process(request, file_count=1)
        allowed = set(tool.get("extensions", {".pdf"}))
        from features.tools.services import file_handler

        file_handler.validate_file(upload, limits.max_file_mb, allowed)
        data = upload.read()
        doc = fitz.open(stream=data, filetype="pdf")
        pages = []
        for i in range(min(doc.page_count, 50)):
            page = doc[i]
            mat = fitz.Matrix(0.25, 0.25)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            buf = io.BytesIO()
            pix.save(buf, "jpeg", jpg_quality=60)
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            pages.append({"index": i, "thumb": b64})
        doc.close()
        return render(
            request,
            "partials/_pdf_page_grid.jinja",
            {"pages": pages, "tool": tool, "mode": tool_slug},
            status=200,
        )
    except UpgradeRequired as exc:
        return _render_partial(
            request,
            "partials/_upgrade_prompt.jinja",
            {"message": exc.message},
        )
    except FileValidationError as exc:
        return _render_partial(
            request,
            "partials/_tool_error.jinja",
            {"tool": tool, "message": exc.message},
        )
