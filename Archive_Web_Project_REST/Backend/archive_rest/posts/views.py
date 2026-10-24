from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from .models import Post
from .permissions import IsManagerOrReadOnly
from .serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsManagerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        params = self.request.query_params
        queryset = Post.objects.select_related("department").prefetch_related(
            "authors__profile", "supervisors__profile"
        )

        if params.get("mine") and user.is_authenticated:
            return queryset.filter(Q(authors=user) | Q(supervisors=user)).distinct()

        if self.action == "list":
            queryset = queryset.filter(is_approved=True)
        elif user.is_authenticated and not user.is_staff:
            queryset = queryset.filter(Q(is_approved=True) | Q(authors=user) | Q(supervisors=user))
        elif not user.is_staff:
            queryset = queryset.filter(is_approved=True)

        if department := params.get("department"):
            queryset = queryset.filter(department__slug=department)
        if year := params.get("year"):
            queryset = queryset.filter(year=year) if year.isdigit() else queryset.none()
        if search := params.get("search", "").strip():
            people = Q()
            for relation in ["authors", "supervisors"]:
                people |= Q(**{f"{relation}__first_name__icontains": search})
                people |= Q(**{f"{relation}__last_name__icontains": search})
                people |= Q(**{f"{relation}__username__icontains": search})
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search) | people
            )
        return queryset.distinct()
