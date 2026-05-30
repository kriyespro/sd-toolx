from django.urls import path
from growth.views import short_link_redirect

urlpatterns = [
    path("", short_link_redirect, {"code": ""}),
]
