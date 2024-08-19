from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


    
    
from django.shortcuts import render
from departments.models import Department
from posts.models import Post, Wishlist
from django.shortcuts import render, get_object_or_404
from posts.models import Post, CustomTag

@login_required
def home(request, tag_slug=None, dept_slug=None):
    data = Post.objects.filter(is_approved=True)
    files = Post.objects.filter(is_approved=True)
    wishlist = []
    dept = Department.objects.all()
    
    selected_dept = None

    if dept_slug is not None:
        selected_dept = get_object_or_404(Department, slug=dept_slug)
        data = Post.objects.filter(department=selected_dept)

    # if request.user.is_authenticated:
    #     wishlist = Wishlist.objects.get(user=request.user).posts.all()

    if tag_slug is not None:
        tag = get_object_or_404(CustomTag, slug=tag_slug)
        data = Post.objects.filter(tags__in=[tag], is_approved=True)
        
    tags = CustomTag.objects.all()
    return render(request, 'home.html', {
        'data': data, 
        'files': files, 
        'tags': tags, 
        'wishlist_posts': wishlist,
        'dept': dept,
        })



def search_posts(request):
    query = request.GET.get('q')
    if query:
        data = Post.objects.filter(title__icontains=query, is_approved=True)
    else:
        data = Post.objects.filter(is_approved=True)
    
    context = {
        'data': data,
        'query': query,
    }
    return render(request, 'search_posts.html', context)
from django.db.models import Q

def search_by_supervisor(request):
    query = request.GET.get('supervisor')
    if query:
        posts = Post.objects.filter(
            Q(supervisors__first_name__icontains=query) | 
            Q(supervisors__last_name__icontains=query), 
            is_approved=True
        ).distinct()
    else:
        posts = Post.objects.filter(is_approved=True)
    
    context = {
        'posts': posts,
        'query': query,
    }
    return render(request, 'search_by_supervisor.html', context)

def search_by_year(request):
    query = request.GET.get('year')
    if query:
        posts = Post.objects.filter(year=query, is_approved=True)
    else:
        posts = Post.objects.filter(is_approved=True)
    
    context = {
        'posts': posts,
        'query': query,
    }
    return render(request, 'search_by_year.html', context)


from django.http import FileResponse
from django.shortcuts import get_object_or_404
import os
def download_file(request, post_id):
    post_file = get_object_or_404(Post, pk=post_id)
    file_path = post_file.file.path
    file_name = os.path.basename(file_path)
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = f'attachment; filename="{file_name}"' 
    return response