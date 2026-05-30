"""Marketing / public views."""
from django.shortcuts import render

from features.tools.registry import live_tools

TOOL_ICONS = {
    "compress-pdf":       ("bg-red-100 dark:bg-red-900/40 text-red-600 dark:text-red-400", "M19 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2zm-7 4v-4m0 0H9m3 0h3"),
    "merge-pdf":          ("bg-orange-100 dark:bg-orange-900/40 text-orange-600 dark:text-orange-400", "M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7"),
    "split-pdf":          ("bg-yellow-100 dark:bg-yellow-900/40 text-yellow-600 dark:text-yellow-400", "M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"),
    "pdf-to-jpg":         ("bg-green-100 dark:bg-green-900/40 text-green-600 dark:text-green-400", "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"),
    "word-to-pdf":        ("bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400", "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"),
    "compress-image":     ("bg-purple-100 dark:bg-purple-900/40 text-purple-600 dark:text-purple-400", "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"),
    "remove-background":  ("bg-pink-100 dark:bg-pink-900/40 text-pink-600 dark:text-pink-400", "M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"),
    "sign-pdf":           ("bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400", "M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"),
    "qr-generator":       ("bg-teal-100 dark:bg-teal-900/40 text-teal-600 dark:text-teal-400", "M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"),
    "ai-summarize-pdf":   ("bg-violet-100 dark:bg-violet-900/40 text-violet-600 dark:text-violet-400", "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"),
    "img-to-pdf":         ("bg-cyan-100 dark:bg-cyan-900/40 text-cyan-600 dark:text-cyan-400", "M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"),
    "protect-pdf":        ("bg-red-100 dark:bg-red-900/40 text-red-600 dark:text-red-400", "M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"),
    "watermark-pdf":      ("bg-amber-100 dark:bg-amber-900/40 text-amber-600 dark:text-amber-400", "M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"),
    "ocr":                ("bg-lime-100 dark:bg-lime-900/40 text-lime-600 dark:text-lime-400", "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"),
    "resize-image":       ("bg-sky-100 dark:bg-sky-900/40 text-sky-600 dark:text-sky-400", "M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"),
}

DEFAULT_ICON = ("bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400", "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z")


def home(request):
    tools = live_tools()
    featured_slugs = [
        "compress-pdf", "merge-pdf", "split-pdf", "pdf-to-jpg",
        "word-to-pdf", "remove-background", "sign-pdf", "qr-generator",
        "compress-image", "ai-summarize-pdf", "img-to-pdf", "protect-pdf",
    ]
    featured = []
    tools_by_slug = {t["slug"]: t for t in tools}
    for slug in featured_slugs:
        if slug in tools_by_slug:
            t = tools_by_slug[slug]
            icon_cls, icon_path = TOOL_ICONS.get(slug, DEFAULT_ICON)
            featured.append({**t, "icon_cls": icon_cls, "icon_path": icon_path})

    categories = [
        {"name": "PDF Tools", "slug": "pdf", "icon_path": "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z", "color": "indigo", "count": sum(1 for t in tools if t["category"] == "pdf")},
        {"name": "Image Tools", "slug": "image", "icon_path": "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z", "color": "violet", "count": sum(1 for t in tools if t["category"] == "image")},
        {"name": "Utilities", "slug": "utility", "icon_path": "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z", "color": "teal", "count": sum(1 for t in tools if t["category"] == "utility")},
    ]

    return render(request, "pages/home.jinja", {
        "featured_tools": featured,
        "tools_count": len(tools),
        "categories": categories,
    })


def text_case_converter(request):
    return render(request, "pages/tools/text_case_converter.jinja")


def json_formatter(request):
    return render(request, "pages/tools/json_formatter.jinja")


def password_generator(request):
    return render(request, "pages/tools/password_generator.jinja")
