from django.urls import path
from django.shortcuts import render


def api_docs(request):
    return render(request, "pages/api_docs.jinja")


urlpatterns = [
    path("", api_docs, name="api-docs"),
]
