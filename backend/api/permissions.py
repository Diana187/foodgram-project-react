from rest_framework import permissions


class AnonReadOnly(permissions.BasePermission):
    """Разрешены только безопасные запросы.
    Доступно без токена."""

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS


class AuthorOrReadOnly(permissions.BasePermission):
    """Изменять и удалять объект может
    его автор или админ."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return (
                request.user == obj.author
                or request.user.is_admin
            )
        return super().has_object_permission(request, view, obj)


class AdminOrReaOnly(permissions.BasePermission):
    """Разрешает доступ к списку или объекту
    только пользователям с ролью admin.
    Также доступ имеют суперюзеры, остальные читают."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_staff
                or request.user.is_superuser
            )
        )


class AdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    """Разрешает доступ к списку или объекту только для чтения.
    Небезопасные запросы доступны только пользователям
    с ролью admin и суперюзерам."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
        )


class IsAdmin(permissions.IsAdminUser):
    """Разрешает доступ к списку или объекту только
    авторизованным пользователям с ролью admin и суперюзерам."""

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )
