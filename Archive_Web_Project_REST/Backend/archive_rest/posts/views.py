from rest_framework import viewsets, permissions
from . import models
from . import serializers

class PostViewset(viewsets.ModelViewSet):
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):

        serializer.save(authors=[self.request.user])

    def perform_update(self, serializer):

        instance = self.get_object()
        if self.request.user not in instance.authors.all() and self.request.user not in instance.supervisors.all():
            raise PermissionError("You do not have permission to edit this post.")
        serializer.save()

    def perform_destroy(self, instance):
  
        if self.request.user not in instance.authors.all() and self.request.user not in instance.supervisors.all():
            raise PermissionError("You do not have permission to delete this post.")
        instance.delete()