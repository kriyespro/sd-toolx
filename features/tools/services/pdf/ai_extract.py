"""AI extract structured data from PDF (names, dates, amounts)."""
import json

import fitz
from django.conf import settings

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError


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
                    "Extract structured data from the document. Return JSON with keys: "
                    "names (list), dates (list), amounts (list with currency), "
                    "addresses (list), organizations (list), key_facts (list of short strings). "
                    "Return only valid JSON, no markdown."
                ),
            },
            {"role": "user", "content": snippet},
        ],
        max_tokens=1500,
    )

    raw = resp.choices[0].message.content.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"raw_extraction": raw}

    out = file_handler.output_path(job, "extracted_data.json")
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    out_rel = file_handler.to_relative(out)

    return {
        "output_file": out_rel,
        "compression_stat": {"fields_extracted": len(data), "chars_processed": len(snippet)},
        "preview_file": "",
        "extracted_data": data,
    }
