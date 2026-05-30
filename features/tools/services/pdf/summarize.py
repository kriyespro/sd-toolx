"""AI PDF summarizer."""
import fitz
from django.conf import settings

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.progress import set_progress


def _extract_text(pdf_path, max_chars: int) -> str:
    doc = fitz.open(pdf_path)
    parts = []
    total = 0
    for page in doc:
        text = page.get_text()
        if not text.strip():
            continue
        parts.append(text)
        total += len(text)
        if total >= max_chars:
            break
    doc.close()
    return "\n\n".join(parts)[:max_chars]


def run(job: ToolJob) -> dict:
    api_key = getattr(settings, "OPENAI_API_KEY", "") or ""
    if not api_key:
        raise ToolError(
            "AI summarizer is not configured yet. Add OPENAI_API_KEY to enable this tool."
        )

    set_progress(job, 15, "Reading PDF…")
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)

    is_pro = False
    if job.user and job.user.is_authenticated:
        try:
            profile = job.user.profile
            plan = profile.plan
            is_pro = profile.is_on_trial or (
                plan is not None and plan.slug in ("pro", "business", "basic")
            )
        except Exception:
            pass

    max_chars = 50000 if is_pro else 2500
    text = _extract_text(src, max_chars)
    if len(text.strip()) < 50:
        raise ToolError("Not enough text in this PDF to summarize.")

    set_progress(job, 35, "Sending to AI…")

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Summarize the document. Return exactly: "
                        "5 bullet points (each starting with •), then a blank line, "
                        "then one short paragraph summary."
                    ),
                },
                {"role": "user", "content": text},
            ],
            max_tokens=800,
        )
        summary = response.choices[0].message.content.strip()
    except Exception as exc:
        raise ToolError(f"AI request failed: {exc}") from exc

    set_progress(job, 85, "Saving summary…")
    out = file_handler.output_path(job, "summary.txt")
    out.write_text(summary, encoding="utf-8")
    out_rel = file_handler.to_relative(out)

    if not is_pro:
        summary += "\n\n— Upgrade to Pro for full-document summaries."

    return {
        "output_file": out_rel,
        "compression_stat": {
            "summary": summary,
            "chars_processed": len(text),
        },
        "preview_file": "",
    }
