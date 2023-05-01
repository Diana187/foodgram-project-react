from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    message = 'Изменение чужого контента запрещено!'

    def has_object_permission(self, request, view, object):
        return (request.method in permissions.SAFE_METHODS
                or object.author == request.user)
