from django.contrib import admin

from recipe.models import (
    Favorite, FavoriteShoppingList, Ingredient,
    RecipeIngredientAmount, Recipe, ShoppingList, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
    )
    list_filter = (
        'author',
        'name',
        'tags',
    )
    search_fields = (
        'author',
        'name',
        'tags',
    )
 # на странице рецепта: общее число добавления рецепта в избранное


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measure',
    )
    list_filter = (
        'name',
    )
    search_fields = (
        'name',
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
         'name',
         'color',
    )
    list_filter = (
        'name',
    )
    search_fields = (
        'name',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    list_filter = (
        'user',
    )
    search_fields = (
        'user',
    )


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    list_filter = (
        'user',
    )
    search_fields = (
        'user',
    )
