from django.db.models import Count, Q
from rest_framework import viewsets

from .models import Department
from .serializers import DepartmentSerializer


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DepartmentSerializer
    pagination_class = None
    queryset = Department.objects.annotate(
        post_count=Count("post", filter=Q(post__is_approved=True))
    )
