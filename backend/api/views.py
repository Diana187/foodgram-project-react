from rest_framework import viewsets
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from api.filters import IngredientFilter, RecipeFilter
from api.serializers import (
    IngredientSerializer, RecipeSerializer, TagSerializer)
from api.paginators import RecipePagination
from recipe.models import (
    Favorite, Ingredient, RecipeIngredientAmount,
    Recipe, ShoppingList, Tag)


class IngredientApiViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = RecipePagination
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (IngredientFilter, )
    search_fields = ('name', )
    # search_fields = ('^name', )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = (IngredientFilter, )
    search_fields = ('name', )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Ingredient.
    Предоставляет возможности получения списка
    и детальной информации об ингредиентах."""

    filter_backends = (CustomSearchFilter,)
    search_fields = ("^name",)


class RecipeApiViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination


class TagApiViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class FavoriteApiViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    pass

class RecipeIngredientAmountApiViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredientAmount.objects.all()
    pass


class ShoppingListViewSet(viewsets.ModelViewSet):
    queryset = ShoppingList.objects.all()
    pass
