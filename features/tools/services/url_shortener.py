"""URL shortener — create short links."""
import json

import shortuuid
from django.db import IntegrityError

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError


def run(job: ToolJob) -> dict:
    opts = job.options or {}
    url = opts.get("url", "").strip()
    if not url:
        raise ToolError("No URL provided.")
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url

    from growth.models import ShortLink
    code = None
    for _ in range(5):
        candidate = shortuuid.uuid()[:8]
        try:
            ShortLink.objects.create(code=candidate, target_url=url)
            code = candidate
            break
        except IntegrityError:
            continue
    if code is None:
        raise ToolError("Could not generate a unique short code. Please try again.")

    short_url = f"https://sdtoolx.com/s/{code}"
    data = {"code": code, "short_url": short_url, "target_url": url}

    out = file_handler.output_path(job, "shortlink.json")
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    out_rel = file_handler.to_relative(out)

    return {
        "output_file": out_rel,
        "compression_stat": {"short_url": short_url, "code": code},
        "preview_file": "",
        "short_url_data": data,
    }
