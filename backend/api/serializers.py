from django.db import transaction
from rest_framework import serializers, validators

from core.utils_serializers import Base64ImageField
from users.serializers import GetUserSerializer
from recipe.models import Favorite, Ingredient, Recipe, RecipeIngredientAmount, Tag, ShoppingCart


class IngredientSerializer(serializers.ModelSerializer):
# модель Ingredient для всех полей

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit', 'created',
                  'updated', )


class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
# общее количество ингридиентов 
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True,
    )
    name = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True,
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True,
    )

    class Meta:
        model = RecipeIngredientAmount
        fields = (
            'id', 'name',
            'measurement_unit', 'amount',
        )


class CreateRecipeIngredientAmountSerializerSerializer(serializers.ModelSerializer):
# создание ингредиентов в рецепте
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredientAmount
        fields = ('id', 'amount', )

    def to_representation(self, instance):
# отображает поля:'id', 'name', 'measurement_unit', 'amount'

        serializer = RecipeIngredientAmountSerializer(instance)
        return serializer.data



class TagSerializer(serializers.ModelSerializer):
# сериализатор для всех полей
    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug',
                  'created', 'updated', )


class GetRecipeSerializer(serializers.ModelSerializer):
# получение списка рецептов, только для чтения
    author = GetUserSerializer(read_only=True)
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    ingredients = RecipeIngredientAmountSerializer(
        many=True,
        read_only=True,
        source='recipes'
    )
    image = Base64ImageField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time',
        )
    
    def get_is_favorited(self, object):
# находится ли рецепт в избранном
        return object.id in self.context['favorite_recipes']

    def get_is_in_shopping_cart(self, object):
# находится ли рецепт в списке покупок
        return object.id in self.context['shopping_cart']


class CreateRecipeSerializer(serializers.ModelSerializer):
# создание рецепта
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    author = GetUserSerializer(read_only=True)
    ingredients = CreateRecipeIngredientAmountSerializerSerializer(
        many=True,
        source='ingredients',
    )
    image = Base64ImageField(required=False, allow_null=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')
    
    def validate(self, object):
        if not object.get('tags'):
            raise serializers.ValidationError(
                'Должен быть указан хотя бы один тег.'
            )
        if not object.get('ingredients'):
            raise serializers.ValidationError(
                'Должен быть указан хотя бы один ингридиент.'
            )
        # if not object.get('cooking_time'):
        #     raise serializers.ValidationError(
        #         'Укажите время приготовления')
        return object

    @transaction.atomic
    def tags_and_ingredients_set(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        RecipeIngredientAmount.objects.bulk_create(
            [RecipeIngredientAmount(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )
    
    @transaction.atomic
    def create(self, validated_data):
# создает новый объект рецепта
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        self.tags_and_ingredients_set(recipe, tags, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
# обновляет существующий объект рецепта
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        RecipeIngredientAmount.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()
        self.tags_and_ingredients_set(instance, tags, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return GetRecipeSerializer(
            instance, context=self.context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
# сериализатор корзины

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)

    def create(self, validated_data):
        if ShoppingCart.objects.filter(
                user=validated_data['user'],
                recipe=validated_data['recipe']).exists():
            raise serializers.ValidationError(
                'Вы уже добавили рецепт в список покупок'
            )
        return ShoppingCart.objects.create(**validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
# избранное
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
            )
        ]

    def to_representation(self, instance):
        return Favorite(instance.recipe).data
