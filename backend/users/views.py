from rest_framework import viewsets

from users.models import Follow, User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
pass
