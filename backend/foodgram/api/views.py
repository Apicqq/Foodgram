from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, \
    IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.mixins import _create_related_object, _delete_related_object
from api.pagination import PageNumberPaginator
from api.permissions import IsAuthorOrReadOnly
from api.serializers import IngredientSerializer, TagSerializer, \
    RecipePostSerializer, RecipeGetSerializer, FavoriteSerializer, \
    ShoppingCartSerializer, GetRemoveSubscriptionSerializer, \
    SubscriptionsListSerializer
from recipes.models import Ingredient, Recipe, Tag, Favorite, ShoppingCart
from users.models import Subscription

User = get_user_model()


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.select_related('author')
    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

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

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        pass


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class UserViewSet(DjoserUserViewSet):
    http_method_names = ('get', 'post', 'delete')
    pagination_class = PageNumberPaginator

    def get_queryset(self):
        if self.action == 'subscriptions':
            return User.objects.filter(following__user=self.request.user)
        return User.objects.all()

    def get_serializer_class(self):
        if self.action in ('post', 'delete'):
            return GetRemoveSubscriptionSerializer
        return SubscriptionsListSerializer

    @action(methods=('get',), detail=False,
            permission_classes=(IsAuthorOrReadOnly,))
    def subscriptions(self, request):
        return self.list(request)

    @action(detail=True, permission_classes=(AllowAny,))
    def subscribe(self, request, pk):
        """blah blah."""

    @subscribe.mapping.post
    def subscribe_to_user(self, request, id):
        return _create_related_object(id, request,
                                      GetRemoveSubscriptionSerializer, author=True)

    @subscribe.mapping.delete
    def unsubscribe_from_user(self, request, id):
        return _delete_related_object(id, request,
                                      Subscription, author=True)
