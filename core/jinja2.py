"""Jinja2 environment for Django's native Jinja2 backend."""
from django.contrib.staticfiles.storage import staticfiles_storage
from django.middleware.csrf import get_token
from django.template.defaultfilters import date as date_filter
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
import jinja2
from jinja2 import Environment


class _JinjaOnlyLoader(jinja2.BaseLoader):
    """Wraps a loader and raises TemplateNotFound for non-.jinja files."""
    def __init__(self, inner):
        self.inner = inner

    def get_source(self, environment, template):
        if not template.endswith(".jinja"):
            raise jinja2.TemplateNotFound(template)
        return self.inner.get_source(environment, template)

    def list_templates(self):
        return [t for t in self.inner.list_templates() if t.endswith(".jinja")]


def environment(**options):
    if "loader" in options:
        options["loader"] = _JinjaOnlyLoader(options["loader"])
    env = Environment(**options)
    env.globals.update(
        {
            "static": static,
            "url": reverse,
            "now": timezone.now,
            "get_csrf": lambda request: get_token(request) if request else "",
        }
    )
    env.filters["date"] = date_filter
    return env
