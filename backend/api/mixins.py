from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.viewsets import GenericViewSet


class CustomUserViewSet(CreateModelMixin,
                        RetrieveModelMixin,
                        ListModelMixin,
                        GenericViewSet):
# для работы с пользователями
    pass