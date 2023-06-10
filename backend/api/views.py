from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import RecipePagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CreateRecipeSerializer, FavoriteSerializer,
                             IngredientSerializer, ShoppingCartSerializer,
                             TagSerializer)
from core.utils import check_and_delete_item
from recipe.models import (Favorite, Ingredient, Recipe,
                           RecipeIngredientAmount, ShoppingCart, Tag)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов.
    Предоставляет возможность получения списка
    и детальной информации об ингредиентах."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (IngredientFilter, )
    search_fields = ('^name', )


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipe. Предоставляет возможности просмотра,
    создания, изменения и удаления рецептов.
    Позволяет добавлять/удалять рецепты из избранного
    Добавлять/удалять рецепт из списка покупок
    Скачивать список ингредиентов для рецепта."""

    queryset = Recipe.objects.all()
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    filterset_fields = ('tags',)
    permission_classes = (IsAuthorOrReadOnly, )

    def get_serializer_class(self):
        if self.action == 'favorite' or self.action == 'shopping_cart':
            return FavoriteSerializer
        return CreateRecipeSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        author = self.request.user
        if self.request.GET.get('is_favorited'):
            favorite_recipes_ids = Favorite.objects.filter(
                user=author).values('recipe_id')

            return queryset.filter(pk__in=favorite_recipes_ids)

        if self.request.GET.get('is_in_shopping_cart'):
            cart_recipes_ids = ShoppingCart.objects.filter(
                user=author).values('recipe_id')
            return queryset.filter(pk__in=cart_recipes_ids)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @staticmethod
    def send_file(ingredients):
        """Выгружает ингредиенты из списка покупок в файл shopping_list.txt."""
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
        """Формирует список покупок из ингредиентов рецепта,
        считает количество ингредиентов."""
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
        """Добавляет и удаляет рецепт из списа покупок."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {
            'user': user.pk,
            'recipe': recipe.pk
        }
        serializer = ShoppingCartSerializer(
            data=data,
            context=self.get_serializer_context()
        )
        shopping_list = ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        )
        if request.method == 'POST':
            if shopping_list.exists():
                return Response(
                    {'errors': 'Рецепт уже есть в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            return check_and_delete_item(
                user, recipe, ShoppingCart, 'Этого рецепта нет в списке покупок.'
            )
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated, ),
        url_path='favorite'
    )
    def favorite(self, request, pk):
        """Добавляет и удаляет рецепт из избранного."""
        user = request.user.id
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
            return check_and_delete_item(
                user, recipe, Favorite, 'Этого рецепта нет в избранном.'
            )
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
