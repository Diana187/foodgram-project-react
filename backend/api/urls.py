from django.urls import include, path
from rest_framework import routers

from api.views import IngredientViewSet, TagViewSet, RecipeViewSet
from users.views import UserViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'users', UserViewSet, basename='users')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
