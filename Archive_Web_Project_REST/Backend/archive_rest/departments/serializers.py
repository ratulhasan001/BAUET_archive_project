from rest_framework import serializers

from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    post_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Department
        fields = ["id", "name", "slug", "post_count"]
