from django.contrib import admin
from django.urls import path

from api.views import RecipeApiView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/recipelist/', RecipeApiView.as_view())
]
