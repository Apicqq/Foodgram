from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, \
    IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter
from api.serializers import IngredientSerializer, TagSerializer, \
    RecipePostSerializer, RecipeGetSerializer, FavoriteSerializer
from recipes.models import Ingredient, Recipe, Tag, Favorite


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
#

class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')


    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = FavoriteSerializer(context={'request': request}, data={
            'user': request.user.id,
        'recipe': recipe.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if request.method == 'POST':
            Favorite.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not Favorite.objects.filter(user=request.user, recipe=recipe).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True,)
    def shopping_cart(self, request, pk):
        pass

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        pass



class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
