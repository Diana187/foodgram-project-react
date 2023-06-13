from rest_framework import serializers, validators

from core.utils import Base64ImageField
from recipe.models import (Favorite, Ingredient, Recipe,
                           RecipeIngredientAmount, ShoppingCart, Tag)
from users.serializers import CustomUserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для связи ингредиентов и рецепта."""
    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = RecipeIngredientAmount
        fields = (
            'id', 'name',
            'measurement_unit',
            'amount',
        )


class CreateRecipeIngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredientAmount
        fields = ('id', 'amount', )

    def to_representation(self, instance):
        serializer = RecipeIngredientAmountSerializer(instance)
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    """Cериализатор для тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка рецептов, только для чтения."""
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    ingredients = RecipeIngredientAmountSerializer(
        many=True,
        read_only=True,
        source='ingredienttorecipe',
    )
    image = Base64ImageField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'text', 'tags',
            'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'image', 'cooking_time',
        )
        read_only_fields = (
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, object):
        """Возвращает True, если рецепт находится в избранном,
        в противном случае возвращает False."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=user,
            recipe=object
        ).exists()

    def get_is_in_shopping_cart(self, object):
        """Возвращает True, если рецепт находится в списке покупок,
        в противном случае возвращает False."""
        user = self.context['request'].user

        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=user,
            recipe=object
        ).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = CreateRecipeIngredientAmountSerializer(
        many=True,
    )
    image = Base64ImageField(required=False, allow_null=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  )

    def validate(self, object):
        if not object.get('tags'):
            raise serializers.ValidationError(
                'Должен быть указан хотя бы один тег.'
            )
        tags_len = len(object.get('tags'))
        if tags_len == 0:
            raise serializers.ValidationError(
                'Нельзя создать рецепт без тегов.'
            )
        if not object.get('ingredients'):
            raise serializers.ValidationError(
                'Должен быть указан хотя бы один ингредиент.'
            )
        ingredient_set = set()
        for ingredient in object.get('ingredients'):
            ingredient_id = ingredient.get('id')
            if ingredient_id in ingredient_set:
                raise serializers.ValidationError(
                    'Найден дубликат ингредиента.'
                )
            ingredient_set.add(ingredient_id)
        if not object.get('cooking_time'):
            raise serializers.ValidationError(
                'Укажите время приготовления.')
        if object['cooking_time'] <= 0:
            raise serializers.ValidationError({
                'Время приготовления не может быть отрицательным.'
            })
        
        return object

    def many_to_many_tag_ingredients(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        RecipeIngredientAmount.objects.bulk_create(
            [RecipeIngredientAmount(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        """Создает новый объект рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.many_to_many_tag_ingredients(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет объект рецепта."""
        tags = validated_data.pop('tags')
        RecipeIngredientAmount.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        self.many_to_many_tag_ingredients(instance, tags, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return GetRecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart'
    )

    def get_is_in_shopping_cart(self, validated_data):
        return ShoppingCart.objects.filter(
            user=validated_data.user,
            recipe=validated_data.recipe
        ).exists()

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe', 'is_in_shopping_cart', )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe', )
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
            )
        ]
