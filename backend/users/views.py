from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.pagination import RecipePagination
from users.models import Follow, User
from users.serializers import (CreateUserSerializer, CustomUserSerializer,
                               FollowSerializer, GetFollowSerializer)


class UserViewSet(UserViewSet):
    """вьюсет для пользователя """
    queryset = User.objects.all()
    permission_classes = (AllowAny, )
    pagination_class = RecipePagination

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated, ),
        pagination_class = (RecipePagination, )
    )
    def me(self, request):
        """возвращает данные пользователя"""
        return Response(
            self.get_serializer(request.user).data,
            status=status.HTTP_200_OK,
        )
    
    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        """список пользователей, на которых подписан"""
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = GetFollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
    
    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, **kwargs):
        """подписывает или отписывает автора на другого пользователя"""
        user = request.user
        author = get_object_or_404(User, id=kwargs['id'])
        data={
            'user': user.id,
            'following': author.id
        }
        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        following = Follow.objects.filter(
            following=author,
            user=user,
        )
        if request.method == 'POST':
            if following.exists():
                return Response(
                    {'errors': 'Нельзя повторно подписаться на автора.'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )    
        if request.method == 'DELETE':
            if not Follow.objects.filter(user=user, following=author):
                return Response(
                    {'errors': 'У вас нет такой подписки.'},
                    status=status.HTTP_400_BAD_REQUEST
            )
            Follow.objects.get(user=user, following=author).delete()
            return Response(
                {'detail': 'Подписка отменена.'},
                status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
