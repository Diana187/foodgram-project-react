from rest_framework import generics

from api.serializers import IngridientSerializer, RecipeSerializer, TagSerializer
from api.paginators import RecipePagination
from recipe.models import Ingridient, Recipe, Tag


class IngridientApiView(generics.ListAPIView):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer


class RecipeApiView(generics.ListAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination


class TagApiView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
