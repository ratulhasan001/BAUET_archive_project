from rest_framework import permissions


class IsManagerOrReadOnly(permissions.BasePermission):
    message = "Only the authors or supervisors of this post can change it."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.is_managed_by(request.user)
