import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipe.models import Recipe


class Base64ImageField(serializers.ImageField):
# картинка
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)

#  нужен?
class RecipeSimpleSerializer(serializers.ModelSerializer):
    """Сериализатор для уменьшенного представления рецепта"""
    image = Base64ImageField

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time',)


# def add_tags(object, tags):
# # добавляет тэги в рцепт
#       for tag in tags:
#            object.tags.add(tag)


# def add_ingredients(model, object, inredients):
# # добавляет ингридиенты в рцепт
#       for ingredient in inredients:
#            model.objects.get_or_create(
#                  recipe=object,
#                  ingredient=ingredient['id'],
#                  amount=ingredient['amount']
#             )

#  в CreateRecipeSerializer было так, для этого верхние функции
#  @transaction.atomic
#     def create(self, validated_data):
#         ingredint_list = validated_data.pop('ingredient_list')
#         tags = validated_data.pop('tags')
#         author = self.context.get('request').user
#         recipe = Recipe.objects.create(author=author, **validated_data)
#         recipe.save()
#         add_tags(recipe, tags)
#         add_ingredients(AmountIngredientInRecipe, recipe, ingredint_list)

#         return recipe

#     @transaction.atomic
#     def update(self, instance, validated_data):
#         ingredint_list = validated_data.pop('ingredient_list')
#         tags = validated_data.pop('tags')
#         instance.tags.clear()
#         add_tags(instance, tags)
#         instance.ingredient.clear()
#         add_ingredients(AmountIngredientInRecipe, instance, ingredint_list)
#         return super().update(instance, validated_data)
