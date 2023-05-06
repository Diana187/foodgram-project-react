from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.db.models import Count
from rest_framework import serializers, validators

from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model

from core.utils import RecipeSimpleSerializer
from recipe.models import Recipe
from users.models import User, Follow

User = get_user_model()

# class UserSerializer(serializers.ModelSerializer):
class UserSerializer(UserCreateSerializer):
# отображение пользователя
# возвращает поле 'is_subscribed',показывающее,
# подписан ли текущий пользователь на этого пользователя
    is_subscribed = serializers.SerializerMethodField()
    # read_only?

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed', )

    def get_is_subscribed(self, object):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and object.following.filter(user=request.user).exists())


class CreateUserSerializer(serializers.ModelSerializer):
# создание пользователя

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password', )
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(CreateUserSerializer, self).create(validated_data)
    
    # def create(self, validated_data):
    #     password = validated_data.pop('password', None)
    #     instance = self.Meta.model(**validated_data)
    #     if password is not None:
    #         instance.set_password(password)
    #     instance.save()
    #     return instance

class GetFollowSerializer(serializers.ModelSerializer):
# выводит список подписок пользователя
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'is_subscribed',
                  'recipes', 'recipes_count', )
    
    def get_is_subscribed(self, author):
# получение is_subscribed
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and object.following.filter(user=request.user).exists())
    
    def get_recipes_count(self, author):
# количество рецептов в виде целого числа
        amount =  Recipe.objects.filter(author=author).aggregate(count=Count('id'))
        return amount['count']
    
    def get_recipes(self, author):
# получение рецептов пользователя
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes = Recipe.objects.filter(author=author)
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSimpleSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializer.data


class FollowSerializer(serializers.ModelSerializer):
# сериализатор создания подписки
    class Meta:
        model = Follow
        fields = ('user', 'following', )

    # def validate(self, data):
    #     if data['user'] == data['author']:
    #         raise serializers.ValidationError(
    #             'Нельзя подписаться на себя.'
    #         )
    #     return data
    
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


class SetPasswordSerializer(serializers.ModelSerializer):
# смена пароля
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('current_password', 'new_password', )

    def validate_current_password(self, value):
        request = self.context.get('request')
        if request.user.check_password(value):
            return value
        raise serializers.ValidationError(
            'Вы указали неправильный пароль.'
        )

    def validate_new_password(self, value):
        if ('current_password',) == ('new_password',):
            raise serializers.ValidationError(
                'Пароли не должны совпадать.'
            )
        validate_password(value)
        return value
