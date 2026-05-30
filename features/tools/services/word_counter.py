"""Word counter — count words, chars, sentences in text/PDF/docx."""
import re

import fitz

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError


def _count_stats(text: str) -> dict:
    words = len(text.split())
    chars = len(text)
    chars_no_space = len(text.replace(" ", "").replace("\n", ""))
    sentences = max(1, len(re.findall(r"[.!?]+", text)))
    paragraphs = len([p for p in text.split("\n\n") if p.strip()])
    reading_time_sec = max(1, words // 4)
    return {
        "words": words,
        "characters": chars,
        "characters_no_space": chars_no_space,
        "sentences": sentences,
        "paragraphs": paragraphs,
        "reading_time_minutes": round(reading_time_sec / 60, 1),
    }


def run(job: ToolJob) -> dict:
    raw_text = job.options.get("text", "")
    src_rels = job.input_files

    if raw_text:
        text = raw_text
    elif src_rels:
        src = file_handler.to_absolute(src_rels[0])
        ext = src.suffix.lower()
        if ext == ".pdf":
            doc = fitz.open(str(src))
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
        elif ext in (".docx", ".doc"):
            try:
                from docx import Document
                document = Document(str(src))
                text = "\n".join(p.text for p in document.paragraphs)
            except Exception as exc:
                raise ToolError(f"Cannot read document: {exc}") from exc
        elif ext == ".txt":
            text = src.read_text(encoding="utf-8", errors="replace")
        else:
            raise ToolError(f"Unsupported file type: {ext}")
    else:
        raise ToolError("No text or file provided.")

    stats = _count_stats(text)
    out = file_handler.output_path(job, "word_count.json")
    import json
    out.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    out_rel = file_handler.to_relative(out)

    return {
        "output_file": out_rel,
        "compression_stat": stats,
        "preview_file": "",
        "word_count_data": stats,
    }
