from django.urls import include, path
from rest_framework import routers

from api.views import RecipeApiViewSet
from users.views import UserViewSet

router = routers.DefaultRouter()
router.register('recipes', RecipeApiViewSet, basename='recipes')
