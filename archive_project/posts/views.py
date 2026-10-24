from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CommentForm, PostForm
from .models import Post, Wishlist


def get_managed_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if not post.can_manage(request.user):
        raise Http404
    return post


@login_required
def add_post(request):
    form = PostForm(request.POST or None, request.FILES or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        post = form.save()
        messages.success(request, f"“{post.title}” was submitted and is waiting for approval.")
        return redirect("profile")
    return render(request, "add_post.html", {"form": form})


@login_required
def edit_post(request, id):
    post = get_managed_post(request, id)
    form = PostForm(request.POST or None, request.FILES or None, instance=post, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Post updated.")
        return redirect(post)
    return render(request, "edit_post.html", {"form": form, "post": post})


@login_required
def delete_post(request, id):
    post = get_managed_post(request, id)
    if request.method == "POST":
        post.file.delete(save=False)
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect("profile")
    return render(request, "confirm_delete.html", {"post": post})


@login_required
def detail_post(request, id):
    post = get_object_or_404(
        Post.objects.select_related("department").prefetch_related(
            "tags", "authors__profile", "supervisors__profile"
        ),
        pk=id,
    )
    if not post.can_view(request.user):
        raise Http404

    form = CommentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.name = request.user.get_full_name() or request.user.username
        comment.email = request.user.email
        comment.save()
        messages.success(request, "Comment posted.")
        return redirect(post)

    wishlist = getattr(request.user, "wishlist", None)
    context = {
        "post": post,
        "comments": post.comments.all(),
        "comment_form": form,
        "can_manage": post.can_manage(request.user),
        "is_saved": bool(wishlist and wishlist.posts.filter(pk=post.pk).exists()),
    }
    if post.file:
        try:
            context["file_size"] = post.file.size
        except OSError:
            context["file_missing"] = True
    return render(request, "post_details.html", context)


@login_required
@require_POST
def add_to_wishlist(request, post_id):
    post = get_object_or_404(Post, id=post_id, is_approved=True)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist.posts.add(post)
    messages.success(request, "Saved to your reading list.")
    return redirect(post)


@login_required
@require_POST
def remove_from_wishlist(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    wishlist = getattr(request.user, "wishlist", None)
    if wishlist:
        wishlist.posts.remove(post)
    messages.info(request, "Removed from your reading list.")
    next_url = request.POST.get("next")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect(post)
