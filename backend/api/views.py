from rest_framework import generics

from api.serializers import (
    IngredientSerializer, RecipeSerializer, TagSerializer)
from api.paginators import RecipePagination
from recipe.models import (
    Favorite, Ingredient, RecipeIngredientAmount,
    Recipe, ShoppingList, Tag)


class IngredientApiView(generics.ListAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeApiView(generics.ListAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination


class TagApiView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class UserApiView(generics.ListAPIView):
    pass
