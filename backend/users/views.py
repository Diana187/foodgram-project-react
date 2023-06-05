from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny, SAFE_METHODS
from rest_framework.response import Response

from api.mixins import CustomUserViewSet
from api.pagination import RecipePagination
from users.models import Follow
from users.serializers import ( CustomUserSerializer, GetFollowSerializer,
                               FollowSerializer)
#  SetPasswordSerializer, CreateUserSerializer,
# User = get_user_model()

from users.models import User
from djoser.views import UserViewSet

class UserViewSet(UserViewSet):
# вьюсет для пользователя 
    queryset = User.objects.all()
    permission_classes = (AllowAny, )
    pagination_class = RecipePagination
    serializer_class = CustomUserSerializer

    # def get_serializer_class(self):
# возвращает класс сериализатора в зависимости от метода
        # if self.request.method in SAFE_METHODS:
        #     return UserSerializer
        # return CreateUserSerializer
    
    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated, ),
        pagination_class = (RecipePagination, )
    )
    def me(self, request):
# возвращает данные пользователя
        return Response(
            self.get_serializer(request.user).data,
            status=status.HTTP_200_OK,
        )

#     @action(
#         methods=['post'],
#         detail=False,
#         permission_classes=(IsAuthenticated, )
#     )
#     def set_password(self, request):
# # устанавливает новый пароль для пользователя
#         user = self.request.user
#         serializer = SetPasswordSerializer(user, data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(
#                 {'detail': 'Пароль успешно изменен.'},
#                 status=status.HTTP_204_NO_CONTENT
#             )
#         return Response(serializer.errors,
#                         status=status.HTTP_400_BAD_REQUEST)
    
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
            # Follow.objects.create(user=user, following=author)
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
