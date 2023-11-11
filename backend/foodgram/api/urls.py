from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, TagViewSet

v1_router = DefaultRouter()

v1_router.register('ingredients', IngredientViewSet, 'ingredients')
v1_router.register('tags', TagViewSet, 'tags')

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(v1_router.urls)),
]