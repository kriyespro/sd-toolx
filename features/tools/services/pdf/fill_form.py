"""Fill PDF form fields."""
import json

import fitz

from features.tools.models import ToolJob
from features.tools.services import file_handler
from features.tools.services.exceptions import ToolError
from features.tools.services.pdf_utils import render_preview


def run(job: ToolJob) -> dict:
    src_rel = job.input_files[0]
    src = file_handler.to_absolute(src_rel)
    field_values_raw = job.options.get("field_values", "{}")
    out = file_handler.output_path(job, "filled.pdf")

    try:
        field_values = json.loads(field_values_raw) if isinstance(field_values_raw, str) else field_values_raw
    except json.JSONDecodeError:
        field_values = {}

    doc = fitz.open(str(src))
    filled = 0

    for page in doc:
        for widget in page.widgets():
            name = widget.field_name
            if name and name in field_values:
                widget.field_value = str(field_values[name])
                widget.update()
                filled += 1

    doc.bake()
    doc.save(str(out), garbage=3, deflate=True)
    doc.close()

    out_rel = file_handler.to_relative(out)
    return {
        "output_file": out_rel,
        "compression_stat": {"fields_filled": filled},
        "preview_file": render_preview(job, out_rel),
    }
