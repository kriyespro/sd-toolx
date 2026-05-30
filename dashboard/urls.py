from django.urls import path

from dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("api/", views.api_key_page, name="api-key"),
    path("api/regenerate/", views.regenerate_api_key, name="api-key-regenerate"),
]
