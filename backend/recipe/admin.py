from django.contrib import admin

from recipe.models import Ingridient, Recipe, Tag


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


@admin.register(Ingridient)
class IngridientAdmin(admin.ModelAdmin):
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
         
    )
    list_filter = (
        
    )
    search_fields = (
        
    )
