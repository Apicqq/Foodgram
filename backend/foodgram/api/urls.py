from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, TagViewSet, RecipeViewSet, \
    UserSubscriptionsViewSet

v1_router = DefaultRouter()

v1_router.register('ingredients', IngredientViewSet, 'ingredients')
v1_router.register('tags', TagViewSet, 'tags')
v1_router.register('recipes', RecipeViewSet, 'recipes')
# v1_router.register('users', SubscriptionsViewSet, 'users')
# v1_router.register(r'users/(?P<user_id>\d+)/subscribe', SubscribeRelations, 'adddeletesubscription')

urlpatterns = [
    path('users/subscriptions/',
         UserSubscriptionsViewSet.as_view({'get': 'list'})),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(v1_router.urls)),

]