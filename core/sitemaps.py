from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Post
from features.tools.registry import live_tools


class ToolSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return live_tools()

    def location(self, tool):
        return reverse(tool["url_name"])


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Post.objects.filter(is_published=True)

    def location(self, post):
        return reverse("blog:detail", args=[post.slug])

    def lastmod(self, post):
        return post.published_at or post.updated_at


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return ["home", "tools:index", "billing:pricing", "blog:list"]

    def location(self, item):
        return reverse(item)
