from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render

from departments.models import Department
from posts.models import CustomTag, Post

SEARCH_CATEGORIES = [
    ("all", "All fields"),
    ("title", "Title"),
    ("supervisor", "Supervisor"),
    ("student", "Student"),
    ("year", "Year"),
]

PAGE_SIZE = 9


def approved_posts():
    return Post.objects.filter(is_approved=True).select_related("department").prefetch_related("tags")


def paginate(request, queryset):
    return Paginator(queryset, PAGE_SIZE).get_page(request.GET.get("page"))


def person_query(relation, term):
    return (
        Q(**{f"{relation}__first_name__icontains": term})
        | Q(**{f"{relation}__last_name__icontains": term})
        | Q(**{f"{relation}__username__icontains": term})
    )


@login_required
def home(request, dept_slug=None, tag_slug=None):
    posts = approved_posts()
    selected_dept = selected_tag = None

    if dept_slug:
        selected_dept = get_object_or_404(Department, slug=dept_slug)
        posts = posts.filter(department=selected_dept)
    if tag_slug:
        selected_tag = get_object_or_404(CustomTag, slug=tag_slug)
        posts = posts.filter(tags=selected_tag)

    tags = (
        CustomTag.objects.annotate(num_posts=Count("tagged_items"))
        .filter(num_posts__gt=0)
        .order_by("-num_posts", "name")[:15]
    )
    return render(
        request,
        "home.html",
        {
            "page_obj": paginate(request, posts),
            "departments": Department.objects.exclude(slug__isnull=True).exclude(slug=""),
            "tags": tags,
            "selected_dept": selected_dept,
            "selected_tag": selected_tag,
            "total_posts": Post.objects.filter(is_approved=True).count(),
        },
    )


@login_required
def search_posts(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "all")
    posts = approved_posts()

    if query:
        if category == "title":
            posts = posts.filter(title__icontains=query)
        elif category == "supervisor":
            posts = posts.filter(person_query("supervisors", query))
        elif category == "student":
            posts = posts.filter(person_query("authors", query))
        elif category == "year":
            posts = posts.filter(year=query) if query.isdigit() else posts.none()
        else:
            category = "all"
            filters = (
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(tags__name__icontains=query)
                | person_query("authors", query)
                | person_query("supervisors", query)
            )
            if query.isdigit():
                filters |= Q(year=query)
            posts = posts.filter(filters)
        posts = posts.distinct()

    page_obj = paginate(request, posts)
    return render(
        request,
        "search_posts.html",
        {
            "page_obj": page_obj,
            "query": query,
            "category": category,
            "categories": SEARCH_CATEGORIES,
        },
    )


@login_required
def download_file(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if not post.can_view(request.user) or not post.file:
        raise Http404
    try:
        handle = post.file.open("rb")
    except FileNotFoundError:
        raise Http404("File not found.")
    return FileResponse(handle, as_attachment=True, filename=post.file_name)
