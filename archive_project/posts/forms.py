from django import forms
from .models import Post, Comment
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.models import User
from taggit.forms import TagWidget


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'content', 'year', 'file', 'tags', 'department']
        widgets = {
            'tags': TagWidget(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        post = super(PostForm, self).save(commit=False)
        if commit:
            post.save()
        return post


class EditPostForm(forms.ModelForm):
    author_emails = forms.CharField(help_text="Enter author emails separated by commas", required=False)
    supervisor_emails = forms.CharField(help_text="Enter sps emails separated by commas", required=False)

    class Meta:
        model = Post
        fields = ['title', 'content', 'author_emails', 'supervisor_emails', 'year', 'file','department']

    def save(self, commit=True):
        post = super(EditPostForm, self).save(commit=False)
        if commit:
            post.save()

        # Handle author emails without clearing existing authors
        author_emails = self.cleaned_data['author_emails']
        emails = [email.strip() for email in author_emails.split(',') if email.strip()]
        for email in emails:
            try:
                user = User.objects.get(email=email)
                post.authors.add(user)
            except User.DoesNotExist:
                # Handle case where user does not exist
                pass
        supervisor_emails = self.cleaned_data['supervisor_emails']
        emails = [email.strip() for email in supervisor_emails.split(',') if email.strip()]
        for email in emails:
            try:
                user = User.objects.get(email=email)
                post.supervisors.add(user)
            except User.DoesNotExist:
                # Handle case where user does not exist
                pass

        if commit:
            post.save()
        return post


class CommentForm(forms.ModelForm):
    class Meta: 
        model = Comment
        fields = ['name', 'email', 'body']

# class PostForm(forms.ModelForm):
#     author_emails = forms.CharField(help_text="Enter author emails separated by commas", required=False)
#     supervisor_emails = forms.CharField(help_text="Enter sps emails separated by commas", required=False)

#     class Meta:
#         model = Post
#         fields = ['title', 'content', 'category', 'author_emails', 'supervisor_emails', 'year']

#     def save(self, commit=True):
#         post = super(PostForm, self).save(commit=False)
#         if commit:
#             post.save()

#         # Handle author emails without clearing existing authors
#         author_emails = self.cleaned_data['author_emails']
#         emails = [email.strip() for email in author_emails.split(',') if email.strip()]
#         for email in emails:
#             try:
#                 user = User.objects.get(email=email)
#                 post.authors.add(user)
#             except User.DoesNotExist:
#                 # Handle case where user does not exist
#                 pass
#         supervisor_emails = self.cleaned_data['supervisor_emails']
#         emails = [email.strip() for email in supervisor_emails.split(',') if email.strip()]
#         for email in emails:
#             try:
#                 user = User.objects.get(email=email)
#                 post.supervisors.add(user)
#             except User.DoesNotExist:
#                 # Handle case where user does not exist
#                 pass

#         if commit:
#             post.save()
#         return post
