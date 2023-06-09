from api.filters import IngredientFilter, RecipeFilter
from api.pagination import RecipePagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CreateRecipeSerializer, FavoriteSerializer,
                             IngredientSerializer, ShoppingCartSerializer,
                             TagSerializer)
from core.utils import check_and_delete_item
from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipe.models import (Favorite, Ingredient, Recipe,
                           RecipeIngredientAmount, ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response


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
    pagination_class.page_size = 6

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
                f"{ingredient['quantity']}")
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
        ).annotate(quantity=Sum('amount'))
        return self.send_file(ingredients)

    def add_or_delete_recipe(self,
                             request,
                             user,
                             recipe,
                             model_class,
                             serializer_class,
                             error_message):
        """Добавляет или удаляет элемент из модели."""
        data = {
            'user': user.pk,
            'recipe': recipe.pk
        }
        serializer = serializer_class(
            data=data, context=self.get_serializer_context()
        )
        item_list = model_class.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if item_list.exists():
                return Response(
                    {'errors': error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            return check_and_delete_item(
                user, recipe, model_class,
                error_message
            )
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated, ),
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        return self.add_or_delete_recipe(
            request=request, user=user, recipe=recipe,
            model_class=ShoppingCart, serializer_class=ShoppingCartSerializer,
            error_message='Этого рецепта нет в в списке покупок.')

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated, ),
        url_path='favorite'
    )
    def favorite(self, request, pk):
        """Добавляет и удаляет рецепт из избранного."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        return self.add_or_delete_recipe(
            request=request, user=user, recipe=recipe,
            model_class=Favorite, serializer_class=FavoriteSerializer,
            error_message='Этого рецепта нет в избранном.'
        )
