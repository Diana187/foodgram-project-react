from django.contrib import admin

from recipe.models import (Favorite, Ingredient, Recipe,
                           RecipeIngredientAmount, ShoppingCart, Tag)


class IngredientInLine(admin.TabularInline):
    model = RecipeIngredientAmount
    extra = 3
    min_num = 1



@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'cooking_time',
        'get_favorites', 'get_ingredients',
    )
    list_filter = ('author', 'name', 'tags', )
    search_fields = ('author', 'name', 'tags', )
    inlines = (IngredientInLine, )

    def get_favorites(self, object):
        return object.favorites.count()
    get_favorites.short_description = 'Избранное'

    def get_ingredients(self, object):
        return ', '.join([
            ingredients.name for ingredients
            in object.ingredients.all()
        ])
    get_ingredients.short_description = 'ингредиенты'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'id', )
    list_filter = ('name', )
    search_fields = ('name', )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug', 'id', )
    list_filter = ('name', )
    search_fields = ('name', )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', )
    list_filter = ('user', 'recipe', )
    search_fields = ('user', 'recipe', )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', )
    list_filter = ('user', )
    search_fields = ('user', )
