from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, TagViewSet, RecipeViewSet

v1_router = DefaultRouter()

v1_router.register('ingredients', IngredientViewSet, 'ingredients')
v1_router.register('tags', TagViewSet, 'tags')
v1_router.register('recipes', RecipeViewSet, 'recipes')

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(v1_router.urls)),
]