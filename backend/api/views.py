from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,
                                        SAFE_METHODS)

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CreateRecipeSerializer, GetRecipeSerializer,
                             FavoriteSerializer, IngredientSerializer,
                             ShoppingCartSerializer, TagSerializer)
from api.pagination import RecipePagination
# from core.utils_serializers import RecipeSimpleSerializer
from recipe.models import (
    Favorite, Ingredient, RecipeIngredientAmount,
    Recipe, ShoppingCart, Tag)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
# ViewSet для модели Ingredient.
# Предоставляет возможности получения списка
# и детальной информации об ингредиентах
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = RecipePagination
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (IngredientFilter, )
    search_fields = ('^name', )


class TagViewSet(viewsets.ModelViewSet):
#ViewSet для модели Tag.
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


class RecipeViewSet(viewsets.ModelViewSet):

# ViewSet для модели Recipe. Предоставляет возможности просмотра,
# создания, изменения и удаления рецептов.
# Позволяет добавлять/удалять рецепты из избранного
# Добавлять/удалять рецепт из списка покупок
# Скачивать список ингридиентов для рецепта.

    queryset = Recipe.objects.all()
    # serializer_class = CreateRecipeSerializer
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly, )
    # IsAuthenticatedOrReadOnly

    def get_serializer_class(self):
# Определяет сериализатор, используемый для конкретного метода
        # if self.request.method in SAFE_METHODS:
        if self.action in ('list', 'retrieve'):
            return GetRecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context
    
    @staticmethod
    def send_file(ingredients):
#  Выгружает ингридиенты из списка покупок в файл shopping_list.txt
        shopping_list = 'Купить:'
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}")
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated, ),
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
# формирует список покупок из ингридиентов рецепта, считает количество ингридиентов
        user = request.user
        if not user.shopping_cart.exists():
            return Response(
                'В вашей корзине нет рецептов.',
                status=status.HTTP_400_BAD_REQUEST,
            )
        ingredients = RecipeIngredientAmount.objects.filter(
            recipe__shopping_cart__user=user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return self.send_file(ingredients)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated, ),
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
# добавляет и удаляет рецепт из списа покупок
        user=request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {
            'user': user.pk,
            'recipe': recipe.pk
        }
        serializer = ShoppingCartSerializer(
            data=data, context=self.get_serializer_context()
        )
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже есть в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        if request.method == "DELETE":
            if not ShoppingCart.objects.filter(user=user, recipe=recipe):
                return Response(
                    {'errors': 'Этого рецепта нет в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
            )
            ShoppingCart.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated, ),
        url_path='favorite'
    )
    def favorite(self, request, pk):
# добавляет и удаляет рецепт из избранного
        user=request.user.id
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': user,
            'recipe': recipe.id
        }
        serializer = FavoriteSerializer(
            data=data, context=self.get_serializer_context()
        )
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже есть в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if not Favorite.objects.filter(user=user, recipe=recipe):
                return Response(
                    {'errors': 'Этого рецепта нет в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
            )
            Favorite.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
