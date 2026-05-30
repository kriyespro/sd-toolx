from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import Post

POSTS = [
    {
        "title": "How to Compress PDF on Mobile in India (Free)",
        "slug": "compress-pdf-mobile-india",
        "meta_title": "Compress PDF on Mobile India — Free Guide 2026",
        "meta_description": "Step-by-step guide to compress PDF on Android and iPhone in India using free online tools.",
        "content_md": """## Why compress PDF on mobile?

Large PDFs are hard to share on WhatsApp and email. Compressing reduces size while keeping documents readable.

## Steps

1. Open **SD-Toolx Compress PDF** in your browser
2. Tap upload and select your PDF
3. Choose quality (Balanced works for most files)
4. Tap **Compress PDF** and download

## Tips for India

- Use WiFi for files over 10MB
- Free plan: 5 operations per day, 20MB max
- Pro removes limits for heavy users
""",
    },
    {
        "title": "Best Free PDF Tools in 2026 (No Signup)",
        "slug": "best-free-pdf-tools-2026",
        "meta_title": "Best Free PDF Tools 2026 — No Signup | SD-Toolx",
        "meta_description": "Top free PDF tools: compress, merge, split, sign, convert — no signup, no popup ads.",
        "content_md": """## What to look for

- **No popup ads** on the tool page
- **No watermark** on free exports
- **UPI-friendly** pricing in INR

## SD-Toolx free tools

- Compress PDF
- Merge PDF
- Split PDF
- Sign PDF (free e-sign)
- Word to PDF
- QR code generator (UPI supported)
""",
    },
    {
        "title": "How to Convert Word to PDF Free Online",
        "slug": "word-to-pdf-free",
        "meta_title": "Word to PDF Free Online — DOCX Converter",
        "meta_description": "Convert DOCX to PDF online free. No software install needed.",
        "content_md": """## Quick steps

1. Go to **Word to PDF** on SD-Toolx
2. Upload your `.docx` file
3. Click convert and download PDF

Works best when LibreOffice is available on the server; a text fallback is used otherwise.
""",
    },
    {
        "title": "Merge PDF Files Online in 3 Steps",
        "slug": "merge-pdf-online-steps",
        "meta_title": "Merge PDF Online Free — 3 Easy Steps",
        "meta_description": "Combine multiple PDFs into one file online. Free merge tool for India.",
        "content_md": """## 3 steps to merge PDFs

1. Upload 2 or more PDF files
2. Keep upload order (this is your merge order)
3. Click **Merge PDFs** and download

Free users can merge up to 3 files per operation.
""",
    },
    {
        "title": "Sign PDF Online Free in India (E-Signature)",
        "slug": "sign-pdf-free-india",
        "meta_title": "Sign PDF Online Free India — E-Sign",
        "meta_description": "Add your signature to PDF documents online free. No expensive subscription.",
        "content_md": """## Why free e-sign matters

Many tools charge ₹800+/month just to sign PDFs. SD-Toolx offers basic signing free.

## How to sign

1. Upload your PDF
2. Draw your signature on the canvas
3. Click **Sign PDF** and download

Perfect for contracts, forms, and school documents.
""",
    },
]


class Command(BaseCommand):
    help = "Seed blog posts for SEO"

    def handle(self, *args, **options):
        now = timezone.now()
        for data in POSTS:
            Post.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    **data,
                    "is_published": True,
                    "published_at": now,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(POSTS)} blog posts."))
