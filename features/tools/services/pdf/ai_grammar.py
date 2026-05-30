"""AI grammar and spell check on PDF text."""
import fitz
from django.conf import settings

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.pdf_utils import render_preview


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)

    doc = fitz.open(str(src))
    text = "\n".join(page.get_text() for page in doc)
    doc.close()

    if not text.strip():
        raise ToolError("No text found in PDF.")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ToolError("OpenAI package not installed.") from exc

    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if not api_key:
        raise ToolError("OpenAI API key not configured.")

    client = OpenAI(api_key=api_key)
    snippet = text[:4000]

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional proofreader. Review the text for grammar and spelling errors. "
                    "Return a corrected version of the text, then add a section '--- CORRECTIONS ---' "
                    "listing each correction made (original → corrected). Be concise."
                ),
            },
            {"role": "user", "content": snippet},
        ],
        max_tokens=3000,
    )

    corrected = resp.choices[0].message.content

    new_doc = fitz.open()
    for chunk in [corrected[i:i+2000] for i in range(0, len(corrected), 2000)]:
        page = new_doc.new_page()
        page.insert_text((50, 50), chunk, fontsize=11)
    out = file_handler.output_path(job, "grammar_checked.pdf")
    new_doc.save(str(out), garbage=3, deflate=True)
    new_doc.close()

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"chars_checked": len(snippet)},
        "preview_file": render_preview(job, out_rel),
    }
