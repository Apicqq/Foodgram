from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name',
                              lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             queryset=Tag.objects.all(),
                                             to_field_name='slug')
    is_favorited = filters.BooleanFilter(method='_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def _is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return self.queryset.filter(in_favorites__user=self.request.user)
        return queryset

    def _in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return self.queryset.filter(carts__user=self.request.user)
        return queryset
