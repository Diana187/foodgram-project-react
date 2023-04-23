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


class TagApiViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = RecipePagination
    permission_classes = (IsAuthenticatedOrReadOnly, )


class RecipeApiViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    filter_backends = (RecipeFilter, )
