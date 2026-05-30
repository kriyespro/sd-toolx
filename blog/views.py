from django.shortcuts import get_object_or_404, render

from blog.models import Post
from blog.services import render_markdown


def post_list(request):
    posts = Post.objects.filter(is_published=True)
    return render(request, "pages/blog/list.jinja", {"posts": posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    return render(
        request,
        "pages/blog/detail.jinja",
        {"post": post, "content_html": render_markdown(post.content_md)},
    )
