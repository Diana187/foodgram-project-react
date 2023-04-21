from django.contrib import admin

from recipe.models import Ingredient, Recipe, Tag


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
    )


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
