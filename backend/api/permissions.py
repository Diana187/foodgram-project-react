from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    message = 'Создавать и изменять объекты может только их автор.'

    def has_object_permission(self, request, view, object):
        return (
            request.method in SAFE_METHODS or object.author == request.user
        )
