"""Root URL configuration."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core.sitemaps import BlogSitemap, StaticSitemap, ToolSitemap
from core.views import home, text_case_converter, json_formatter, password_generator
from core.views_seo import robots_txt
from growth.views import join_referral, short_link_redirect

sitemaps = {
    "tools": ToolSitemap,
    "blog": BlogSitemap,
    "static": StaticSitemap,
}

urlpatterns = [
    path("", home, name="home"),
    path("robots.txt", robots_txt, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path(f"{settings.ADMIN_URL}", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("users/", include("users.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("billing/", include("billing.urls")),
    path("blog/", include("blog.urls")),
    path("growth/", include("growth.urls")),
    path("join/<str:code>/", join_referral, name="join-referral"),
    path("s/<str:code>/", short_link_redirect, name="short-link"),
    path("tools/", include("features.tools.urls")),
    path("tools/text-case-converter/", text_case_converter, name="text-case-converter"),
    path("tools/json-formatter/", json_formatter, name="json-formatter"),
    path("tools/password-generator/", password_generator, name="password-generator"),
    path("api/", include("features.api.urls")),
    path("api/docs/", include("features.api.doc_urls")),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
