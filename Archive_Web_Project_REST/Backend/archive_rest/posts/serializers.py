from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.serializers import UserSummarySerializer
from departments.models import Department

from .models import Post


class EmailListField(serializers.CharField):
    def to_internal_value(self, data):
        raw = super().to_internal_value(data)
        emails = sorted({e.strip().lower() for e in raw.split(",") if e.strip()})
        users = list(User.objects.filter(email__in=emails))
        missing = set(emails) - {u.email.lower() for u in users}
        if missing:
            raise serializers.ValidationError("No account found for: " + ", ".join(sorted(missing)))
        return users


class PostSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    department_name = serializers.CharField(source="department.name", read_only=True)
    authors = UserSummarySerializer(many=True, read_only=True)
    supervisors = UserSummarySerializer(many=True, read_only=True)
    author_emails = EmailListField(write_only=True, required=False, allow_blank=True)
    supervisor_emails = EmailListField(write_only=True, required=False, allow_blank=True)
    file_name = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "year",
            "department",
            "department_name",
            "file",
            "file_name",
            "is_approved",
            "authors",
            "supervisors",
            "author_emails",
            "supervisor_emails",
            "can_edit",
        ]
        read_only_fields = ["is_approved"]

    def get_file_name(self, post):
        return post.file.name.rsplit("/", 1)[-1] if post.file else None

    def get_can_edit(self, post):
        request = self.context.get("request")
        return bool(request and post.is_managed_by(request.user))

    def create(self, validated_data):
        user = self.context["request"].user
        authors = set(validated_data.pop("author_emails", [])) | {user}
        supervisors = validated_data.pop("supervisor_emails", [])
        post = Post.objects.create(**validated_data)
        post.authors.set(authors)
        post.supervisors.set(supervisors)
        return post

    def update(self, instance, validated_data):
        authors = validated_data.pop("author_emails", None)
        supervisors = validated_data.pop("supervisor_emails", None)
        post = super().update(instance, validated_data)
        if authors is not None:
            user = self.context["request"].user
            if post.authors.filter(pk=user.pk).exists():
                authors = set(authors) | {user}
            post.authors.set(authors)
        if supervisors is not None:
            post.supervisors.set(supervisors)
        return post
