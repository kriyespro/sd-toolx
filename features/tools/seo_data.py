"""SEO metadata for all tools."""
import json

TOOL_SEO = {
    "compress-pdf": {
        "title": "Compress PDF Online Free — Reduce PDF Size Instantly",
        "description": "Compress PDF files online for free. Reduce file size up to 90% with no signup. Fast, secure, India-friendly.",
        "h1": "Compress PDF",
        "h2": "Reduce PDF size in seconds",
        "faq": [
            {
                "q": "How do I compress a PDF for free?",
                "a": "Upload your PDF, choose quality, and click Compress. Download the smaller file instantly.",
            },
            {
                "q": "Is it safe to compress PDF online?",
                "a": "Files are processed securely and auto-deleted after 2 hours. We never share your documents.",
            },
            {
                "q": "What is the maximum file size?",
                "a": "Free users can upload up to 20MB. Pro users can upload up to 200MB.",
            },
        ],
    },
    "merge-pdf": {
        "title": "Merge & Compress PDF Online Free",
        "description": "Merge multiple PDFs into one file and compress automatically. Smaller downloads, free, no signup.",
        "h1": "Merge & Compress PDF",
        "h2": "Combine PDFs and shrink file size in one step",
        "faq": [
            {"q": "How many PDFs can I merge?", "a": "Free plan: up to 3 files. Pro: unlimited files."},
            {
                "q": "Is the merged file compressed?",
                "a": "Yes — we merge your PDFs first, then compress the result so the download is smaller.",
            },
            {"q": "Can I choose compression quality?", "a": "Yes — pick Balanced, Smallest file, or High quality before processing."},
        ],
    },
    "split-pdf": {
        "title": "Split PDF Online Free — Extract PDF Pages",
        "description": "Split PDF by page range online. Extract specific pages free and fast.",
        "h1": "Split PDF",
        "h2": "Extract pages from any PDF",
        "faq": [
            {"q": "How do I split a PDF by pages?", "a": "Enter ranges like 1-3, 5, 7-10 and click Split."},
        ],
    },
    "rotate-pdf": {
        "title": "Rotate PDF Online Free",
        "description": "Rotate PDF pages 90°, 180°, or 270° online for free.",
        "h1": "Rotate PDF",
        "h2": "Fix PDF orientation",
        "faq": [],
    },
    "pdf-to-jpg": {
        "title": "PDF to JPG Converter Free",
        "description": "Convert PDF pages to JPG images online. Free first page, Pro for all pages.",
        "h1": "PDF to JPG",
        "h2": "Convert PDF to images",
        "faq": [],
    },
    "img-to-pdf": {
        "title": "JPG to PDF Converter Free — Images to PDF",
        "description": "Convert JPG, PNG, WebP images to a single PDF online for free.",
        "h1": "JPG to PDF",
        "h2": "Combine images into one PDF",
        "faq": [],
    },
    "word-to-pdf": {
        "title": "Word to PDF Converter Free — DOCX to PDF",
        "description": "Convert Word documents to PDF online free. DOCX to PDF in seconds.",
        "h1": "Word to PDF",
        "h2": "Convert DOCX to PDF",
        "faq": [],
    },
    "compress-image": {
        "title": "Compress Image Lossless Online Free — JPG, PNG, WebP",
        "description": "Lossless image compression online. Strip metadata, optimize PNG/WebP, no visible quality loss.",
        "h1": "Compress Image",
        "h2": "Lossless and maximum compression modes",
        "faq": [
            {
                "q": "What is lossless compression?",
                "a": "Your image looks the same. We remove hidden metadata and re-pack the file more efficiently.",
            },
            {
                "q": "Which output should I pick?",
                "a": "WebP lossless is often the smallest. Keep original format for PNG transparency workflows.",
            },
        ],
    },
    "sign-pdf": {
        "title": "Sign PDF Online Free — E-Signature",
        "description": "Sign PDF documents online for free. Draw your signature — no expensive subscription.",
        "h1": "Sign PDF",
        "h2": "Add your signature to any PDF",
        "faq": [],
    },
    "qr-generator": {
        "title": "QR Code Generator Free — UPI, URL, WhatsApp",
        "description": "Create QR codes for URL, UPI, WhatsApp, and WiFi free. Download instantly.",
        "h1": "QR Code Generator",
        "h2": "Create QR codes in seconds",
        "faq": [],
    },
    "remove-background": {
        "title": "Remove Background from Image Free — AI",
        "description": "Remove image background online. Transparent PNG. Free AI tool for India.",
        "h1": "Remove Background",
        "faq": [
            {"q": "What format is the output?", "a": "PNG with transparent background."},
        ],
    },
    "ai-summarize-pdf": {
        "title": "AI PDF Summarizer — Free Bullet Points",
        "description": "Summarize any PDF with AI. Get 5 bullet points and a short summary instantly.",
        "h1": "AI PDF Summarizer",
        "faq": [
            {"q": "How much of my PDF is summarized?", "a": "Free users: first ~500 words. Pro: full document."},
        ],
    },
}


def get_seo(slug: str) -> dict:
    return TOOL_SEO.get(slug, {})


def build_json_ld(tool: dict, seo: dict, request) -> str:
    url = request.build_absolute_uri()
    data = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": tool.get("name", ""),
        "description": seo.get("description", tool.get("description", "")),
        "url": url,
        "applicationCategory": "UtilitiesApplication",
        "operatingSystem": "Web",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR"},
    }
    faq = seo.get("faq", [])
    if faq:
        faq_ld = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item["q"],
                    "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
                }
                for item in faq
            ],
        }
        return json.dumps([data, faq_ld])
    return json.dumps(data)
