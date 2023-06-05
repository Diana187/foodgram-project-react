# from django.contrib.auth.hashers import make_password
# from django.contrib.auth.password_validation import validate_password
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import serializers, validators

# from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model

from core.utils import RecipeSimpleSerializer
from recipe.models import Recipe
from users.models import User, Follow

from users.models import User
from djoser.serializers import UserSerializer
from rest_framework.fields import SerializerMethodField

class CustomUserSerializer(UserSerializer):
    """отображение пользователя
    возвращает поле 'is_subscribed',показывающее,
    одписан ли текущий пользователь на этого пользователя"""
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if self.context.get('request').user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class FollowRecipeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class GetFollowSerializer(serializers.ModelSerializer):
    """выводит список подписок пользователя"""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        follow = Follow.objects.filter(following=obj, user=request.user)
        return follow.exists()
    
    def get_recipes_count(self, author):
        """количество рецептов в виде целого числа"""
        amount =  Recipe.objects.filter(author=author).aggregate(count=Count('id'))
        return amount['count']

    def get_recipes(self, obj):
        request = self.context['request']
        limit = request.GET.get('recipes_limit')
        author = get_object_or_404(User, id=obj.pk)
        recipes = author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = FollowRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        )
        return serializer.data
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'is_subscribed',
                  'recipes', 'recipes_count', )


class FollowSerializer(serializers.ModelSerializer):
    """сериализатор создания подписки"""
    class Meta:
        model = Follow
        fields = ('user', 'following', )
    
    def validate_following(self, data):
        if self.context.get('request').user == data:
            raise serializers.ValidationError('Нельзя подписаться на себя.')
        return data

    def create(self, validated_data):
        if Follow.objects.filter(
                user=validated_data['user'],
                following=validated_data['following']).exists():
            raise validators.UniqueTogetherValidator(
                'Вы уже подписаны на этого пользователя.'
            )
        return Follow.objects.create(**validated_data)
