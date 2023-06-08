from django_filters import FilterSet
from django_filters import rest_framework as filters
from rest_framework import filters as f

from recipe.models import Ingredient, Recipe, Tag
from users.models import User


class IngredientFilter(f.SearchFilter):
    """Фильтр для ингредиентов: поиск по названию"""
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Класс фильтра для модели Recipe. Позволяет производить
    поиск рецептов по тегам, автору, наличию в списке
    избранного и корзине покупок."""
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author =filters.ModelChoiceFilter(
        queryset=User.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags', 'author',
            'is_favorited', 'is_in_shopping_cart',
        )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset
