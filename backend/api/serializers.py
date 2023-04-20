from rest_framework import serializers

from recipe.models import Ingridient, Recipe, Tag


class IngridientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingridient
        fields = ('name',)


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('name', 'text',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('name',)

