from django.shortcuts import redirect, render
from . import forms
from . import models
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView,UpdateView,DeleteView,DetailView

def sned_mail(user, subject, template):
        message = render_to_string(template, {
            'user' : user,
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()



@login_required
def add_post(request):
    if request.method == 'POST':
        post_form = forms.PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.save()
            post.authors.add(request.user)
            post_form.save_m2m()
            # sned_mail(request.user, "Pending Message", "pa.html")
            return redirect('add_post')
    else:
        post_form = forms.PostForm()
    return render(request, 'add_post.html', {'form': post_form})


@login_required
def edit_post(request, id):
    post = models.Post.objects.get(pk=id)
    if request.method == 'POST':
        post_form = forms.EditPostForm(request.POST, request.FILES, instance=post)
        if post_form.is_valid():
            post_form.save()
            return redirect('homepage')
    else:
        post_form = forms.EditPostForm(instance=post)
    return render(request, 'edit_post.html', {'form': post_form})



@login_required
def delete_post(request, id):
    post = models.Post.objects.get(pk=id)
    post.delete()
    return redirect('homepage')

# @method_decorator(login_required, name='dispatch')
from django.template.defaultfilters import filesizeformat

class DetailPostView(DetailView):
    model = models.Post
    pk_url_kwarg = 'id'
    template_name = 'post_details.html'
    
    def post(self, request, *args, **kwargs):
        comment_form = forms.CommentForm(data=self.request.POST)
        post = self.get_object()
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
        return self.get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object 
        comments = post.comments.all()
        comment_form = forms.CommentForm()

        # Add file name and size to context if file exists
        if post.file:
            file_name = post.file.name.split('/')[-1]  # Get the filename without the path
            file_size = filesizeformat(post.file.size)
            context['file_name'] = file_name
            context['file_size'] = file_size
        
        context['comments'] = comments
        context['comment_form'] = comment_form
        return context



# views.py
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Wishlist
from django.contrib import messages

@login_required
def add_to_wishlist(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    if post in wishlist.posts.all():
        messages.info(request, 'Post already in wishlist.')
    else:
        wishlist.posts.add(post)
        messages.success(request, 'Post added to wishlist.')
    return redirect('homepage')

@login_required
def remove_from_wishlist(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    wishlist = Wishlist.objects.get(user=request.user)
    if post in wishlist.posts.all():
        wishlist.posts.remove(post)
        messages.success(request, 'Post removed from wishlist.')
    else:
        messages.info(request, 'Post not in wishlist.')
    return redirect('profile')

from django.shortcuts import render, get_object_or_404
from .models import Post, CustomTag
from departments.models import Department

def tag_wise_post(request, tag_slug):
    tag = get_object_or_404(CustomTag, slug=tag_slug)
    dept = Department.objects.all()
    posts = Post.objects.filter(tags__in=[tag], is_approved=True)
    return render(request, 'home.html', {'data': posts, 'tag': tag, 'dept': dept,})
