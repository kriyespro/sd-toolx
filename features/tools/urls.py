from django.urls import path

from features.tools import views, views_pages

app_name = "tools"

urlpatterns = [
    path("", views.tools_index, name="index"),
    path("compress-pdf/", views.CompressPdfView.as_view(), name="compress-pdf"),
    path("merge-pdf/", views.MergePdfView.as_view(), name="merge-pdf"),
    path("split-pdf/", views.SplitPdfView.as_view(), name="split-pdf"),
    path("rotate-pdf/", views.RotatePdfView.as_view(), name="rotate-pdf"),
    path("pdf-to-jpg/", views.PdfToJpgView.as_view(), name="pdf-to-jpg"),
    path("img-to-pdf/", views.ImgToPdfView.as_view(), name="img-to-pdf"),
    path("word-to-pdf/", views.WordToPdfView.as_view(), name="word-to-pdf"),
    path("compress-image/", views.CompressImageView.as_view(), name="compress-image"),
    path("sign-pdf/", views.SignPdfView.as_view(), name="sign-pdf"),
    path("pdf-to-word/", views.PdfToWordView.as_view(), name="pdf-to-word"),
    path(
        "<slug:tool_slug>/page-thumbnails/",
        views_pages.page_thumbnails,
        name="page-thumbnails",
    ),
    path("reorder-pdf/", views.ReorderPdfView.as_view(), name="reorder-pdf"),
    path("delete-pdf-pages/", views.DeletePdfPagesView.as_view(), name="delete-pdf-pages"),
    path("unlock-pdf/", views.UnlockPdfView.as_view(), name="unlock-pdf"),
    path("protect-pdf/", views.ProtectPdfView.as_view(), name="protect-pdf"),
    path("remove-background/", views.RemoveBackgroundView.as_view(), name="remove-background"),
    path("ai-summarize-pdf/", views.AiSummarizePdfView.as_view(), name="ai-summarize-pdf"),
    path("qr-generator/", views.QrGeneratorView.as_view(), name="qr-generator"),
    # Phase 5 tools
    path("excel-to-pdf/", views.ExcelToPdfView.as_view(), name="excel-to-pdf"),
    path("ppt-to-pdf/", views.PptToPdfView.as_view(), name="ppt-to-pdf"),
    path("pdf-to-excel/", views.PdfToExcelView.as_view(), name="pdf-to-excel"),
    path("pdf-to-ppt/", views.PdfToPptView.as_view(), name="pdf-to-ppt"),
    path("watermark-pdf/", views.WatermarkPdfView.as_view(), name="watermark-pdf"),
    path("repair-pdf/", views.RepairPdfView.as_view(), name="repair-pdf"),
    path("redact-pdf/", views.RedactPdfView.as_view(), name="redact-pdf"),
    path("compare-pdf/", views.ComparePdfView.as_view(), name="compare-pdf"),
    path("fill-pdf-form/", views.FillPdfFormView.as_view(), name="fill-pdf-form"),
    path("ocr/", views.OcrView.as_view(), name="ocr"),
    path("ai-translate-pdf/", views.AiTranslatePdfView.as_view(), name="ai-translate-pdf"),
    path("ai-extract-data/", views.AiExtractDataView.as_view(), name="ai-extract-data"),
    path("upscale-image/", views.UpscaleImageView.as_view(), name="upscale-image"),
    path("word-counter/", views.WordCounterView.as_view(), name="word-counter"),
    # Phase 6 tools
    path("resize-image/", views.ResizeImageView.as_view(), name="resize-image"),
    path("convert-image/", views.ConvertImageView.as_view(), name="convert-image"),
    path("watermark-image/", views.WatermarkImageView.as_view(), name="watermark-image"),
    path("id-photo/", views.IdPhotoView.as_view(), name="id-photo"),
    path("ai-grammar-check/", views.AiGrammarCheckView.as_view(), name="ai-grammar-check"),
    path("barcode-generator/", views.BarcodeGeneratorView.as_view(), name="barcode-generator"),
    path("url-shortener/", views.UrlShortenerView.as_view(), name="url-shortener"),
    path("job/<int:job_id>/status/", views.job_status, name="job-status"),
    path("job/<int:job_id>/download/", views.job_download, name="job-download"),
    path("recent/", views.recent_files_partial, name="recent-files"),
]
