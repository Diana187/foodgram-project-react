from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from api.mixins import CustomUserViewSet
from api.pagination import RecipePagination
from users.models import Follow
from users.serializers import (CreateUserSerializer, UserSerializer, 
                               SetPasswordSerializer, GetFollowSerializer,
                               FollowSerializer)

User = get_user_model()


class UserViewSet(CustomUserViewSet):
# вьюсет для пользователя 
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, )
    pagination_class = RecipePagination

    def get_serializer_class(self):
# возвращает класс сериализатора в зависимости от метода
        if self.request.method in SAFE_METHODS:
            return UserSerializer
        return CreateUserSerializer
    
    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
# возвращает данные пользователя
        return Response(
            self.get_serializer(request.user).data,
            status=status.HTTP_200_OK,
        )

    @action(
        methods=['post'],
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def set_password(self, request):
# устанавливает новый пароль для пользователя
        # user = self.request.user
        # serializer = SetPasswordSerializer(
        #     data=request.data,
        #     context={'request': request})
        # if serializer.is_valid():
        #     user.set_password(serializer.validated_data['new_password'])
        #     user.save()
        #     return Response(serializer.data, status=status.HTTP_200_OK)
        # return Response(serializer.errors,
        #                 status=status.HTTP_400_BAD_REQUEST)

        user = self.request.user
        serializer = SetPasswordSerializer(user, data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {'detail': 'Пароль успешно изменен'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
    
    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
# список пользователей, на которых подписан
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
# подписывает или отписывает автора на другого пользователя
        user = request.user
        author = get_object_or_404(User, id=kwargs['pk'])
        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        following = Follow.objects.filter(
            author=author,
            user=request.user
        )
        if request.method == 'POST':
            if following.exists():
                return Response(
                    {'errors': 'Нельзя повторно подписаться на автора.'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=request.user, author=author)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
                )
        if request.method == 'DELETE':
            follow = get_object_or_404(Follow, user=user, author=author)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
