
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, \
    IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter
from api.mixins import _create_related_object, _delete_related_object
from api.permissions import IsAdminAuthorOrReadOnly
from api.serializers import IngredientSerializer, TagSerializer, \
    RecipePostSerializer, RecipeGetSerializer, FavoriteSerializer, \
    ShoppingCartSerializer
from recipes.models import Ingredient, Recipe, Tag, Favorite, ShoppingCart


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminAuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """blah blah"""

    @favorite.mapping.post
    def make_recipe_favorite(self, request, pk):
        return _create_related_object(pk, request, FavoriteSerializer)

    @favorite.mapping.delete
    def unmake_recipe_favorite(self, request, pk):
        return _delete_related_object(pk, request, Favorite)

    @action(detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """blah blah"""
    @shopping_cart.mapping.post
    def add_to_shopping_cart(self, request, pk):
        return _create_related_object(pk, request, ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk):
        return _delete_related_object(pk, request, ShoppingCart)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        pass


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
