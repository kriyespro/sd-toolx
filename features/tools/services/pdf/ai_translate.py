"""AI translate PDF text using OpenAI."""
import fitz
from django.conf import settings

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.pdf_utils import render_preview

LANG_NAMES = {
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese (Simplified)",
    "ar": "Arabic",
    "pt": "Portuguese",
}


def _translate_text(text: str, target_lang: str) -> str:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ToolError("OpenAI package not installed.") from exc

    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if not api_key:
        raise ToolError("OpenAI API key not configured.")

    lang_name = LANG_NAMES.get(target_lang, target_lang)
    client = OpenAI(api_key=api_key)

    chunks = [text[i:i+3000] for i in range(0, len(text), 3000)]
    translated_parts = []
    for chunk in chunks[:10]:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Translate the following text to {lang_name}. Preserve formatting. Return only the translation."},
                {"role": "user", "content": chunk},
            ],
            max_tokens=4000,
        )
        translated_parts.append(resp.choices[0].message.content)

    return "\n\n".join(translated_parts)


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    target_lang = job.options.get("target_lang", "hi")
    lang_name = LANG_NAMES.get(target_lang, target_lang)

    doc = fitz.open(str(src))
    pages_text = []
    for page in doc:
        pages_text.append(page.get_text())
    doc.close()

    full_text = "\n\n--- Page Break ---\n\n".join(pages_text)
    if not full_text.strip():
        raise ToolError("No text found in PDF. OCR may be needed first.")

    translated = _translate_text(full_text, target_lang)

    out = file_handler.output_path(job, f"translated_{target_lang}.pdf")
    new_doc = fitz.open()
    for chunk in [translated[i:i+2000] for i in range(0, len(translated), 2000)]:
        page = new_doc.new_page()
        page.insert_text((50, 50), chunk, fontsize=11)
    new_doc.save(str(out), garbage=3, deflate=True)
    new_doc.close()

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"target_language": lang_name, "chars_translated": len(full_text)},
        "preview_file": render_preview(job, out_rel),
    }
