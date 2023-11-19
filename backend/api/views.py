from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (IngredientSerializer,
                             TagSerializer,
                             RecipePostSerializer,
                             RecipeGetSerializer,
                             FavoriteSerializer,
                             ShoppingCartSerializer,
                             GetRemoveSubscriptionSerializer,
                             SubscriptionsListSerializer)
from core.pdf_reporter import draw_pdf_report
from core.services import _create_related_object, _delete_related_object
from recipes.models import (Ingredient,
                            Recipe,
                            Tag,
                            Favorite,
                            ShoppingCart, RecipeIngredient)
from users.models import Subscription, User


class IngredientViewSet(ReadOnlyModelViewSet):
    """ViewSet для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    """ViewSet для работы с рецептами.
    Помимо стандартных методов, реализованы action
    для работы с избранными рецептами пользователя."""

    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Recipe.objects.select_related(
                'author'
            ).prefetch_related(
                'tags',
                'ingredients'
            )
        return Recipe.objects.select_related(
            'author'
        ).prefetch_related(
            'tags',
            'ingredients'
        ).get_recipe_filters(self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(detail=True,
            permission_classes=(IsAuthenticated,), methods=('post',))
    def favorite(self, request, pk):
        """Добавление и удаление рецептов из избранного."""
        return _create_related_object(pk, request, FavoriteSerializer)

    @favorite.mapping.delete
    def unmake_recipe_favorite(self, request, pk):
        return _delete_related_object(pk, request, Favorite)

    @action(detail=True,
            permission_classes=(IsAuthenticated,), methods=('post',))
    def shopping_cart(self, request, pk):
        """Добавление и удаление рецептов из списка покупок."""
        return _create_related_object(pk, request, ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk):
        return _delete_related_object(pk, request, ShoppingCart)

    @action(methods=('get',), detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shoppingcarts__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
            ).annotate(
                ingredient_amount=Sum(
                    'amount'
                )
            )
        )
        return draw_pdf_report(ingredients)


class TagViewSet(ReadOnlyModelViewSet):
    """ViewSet для работы с тэгами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = None


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с подписками. Наследуемся от
    вьюсета Djoser'а, чтобы соблюсти логику путей в API."""

# Для экшена 'me' у меня установлен дефолтный пермишен в настройках Djoser.

    @action(methods=('get',), detail=False,
            permission_classes=(IsAuthenticated,),
            serializer_class=SubscriptionsListSerializer)
    def subscriptions(self, request):
        queryset = self.filter_queryset(
            User.objects.filter(following__user=self.request.user)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, permission_classes=(IsAuthenticated,),
            methods=('post',))
    def subscribe(self, request, id):
        """Action для работы с подписками пользователей."""
        serializer = GetRemoveSubscriptionSerializer(
            data={
                'user': request.user.id,
                'author': id},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        if not Subscription.objects.filter(
                user=request.user, author_id=id).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Subscription.objects.filter(
            user=request.user, author=id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
