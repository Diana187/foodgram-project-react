from rest_framework import generics

from api.serializers import (
    IngredientSerializer, RecipeSerializer, TagSerializer)
from api.paginators import RecipePagination
from recipe.models import (
    Favorite, FavoriteShoppingList, Ingredient,
    RecipeIngredientAmount, Recipe, ShoppingList, Tag)


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


class FavoriteApiView(generics.ListAPIView):
    queryset = Favorite.objects.all()
    pass


class FavoriteShoppingListApiView(generics.ListAPIView):
    queryset = FavoriteShoppingList.objects.all()
    pass


class IngredientRecipeApiView(generics.ListAPIView):
    queryset = RecipeIngredientAmount.objects.all()
    pass


class ShoppingListApiView(generics.ListAPIView):
    queryset = ShoppingList.objects.all()
    pass