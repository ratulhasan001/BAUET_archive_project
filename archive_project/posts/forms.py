from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from taggit.forms import TagWidget

from core.forms import StyledFormMixin

from .models import Comment, Post


def parse_emails(raw):
    return sorted({email.strip().lower() for email in raw.split(",") if email.strip()})


class PostForm(StyledFormMixin, forms.ModelForm):
    author_emails = forms.CharField(
        label="Co-author emails",
        required=False,
        help_text="Comma separated. Each person must already have an account.",
    )
    supervisor_emails = forms.CharField(
        label="Supervisor emails",
        required=False,
        help_text="Comma separated. Each person must already have an account.",
    )

    class Meta:
        model = Post
        fields = ["title", "content", "department", "year", "tags", "file"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 6}),
            "tags": TagWidget(attrs={"placeholder": "machine learning, iot, web"}),
        }
        help_texts = {"tags": "Comma separated keywords."}

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["year"].widget.attrs.update({"min": 2000, "max": timezone.now().year + 1})
        self.fields["department"].empty_label = "Select a department"
        if self.instance.pk:
            self.fields["file"].required = False
            self.initial["author_emails"] = ", ".join(
                self.instance.authors.exclude(pk=user.pk).values_list("email", flat=True)
            )
            self.initial["supervisor_emails"] = ", ".join(
                self.instance.supervisors.values_list("email", flat=True)
            )

    def _users_for(self, field_name):
        emails = parse_emails(self.cleaned_data.get(field_name, ""))
        users = list(User.objects.filter(email__in=emails))
        missing = set(emails) - {u.email.lower() for u in users}
        if missing:
            raise forms.ValidationError(
                "No account found for: " + ", ".join(sorted(missing))
            )
        return users

    def clean_author_emails(self):
        return self._users_for("author_emails")

    def clean_supervisor_emails(self):
        return self._users_for("supervisor_emails")

    def save(self, commit=True):
        is_new = self.instance.pk is None
        post = super().save(commit=commit)
        if commit:
            authors = set(self.cleaned_data["author_emails"])
            if is_new or post.authors.filter(pk=self.user.pk).exists():
                authors.add(self.user)
            post.authors.set(authors)
            post.supervisors.set(self.cleaned_data["supervisor_emails"])
        return post


class CommentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        labels = {"body": "Add a comment"}
        widgets = {"body": forms.Textarea(attrs={"rows": 3, "placeholder": "Share your thoughts..."})}
