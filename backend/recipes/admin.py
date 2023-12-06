from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.forms import models
from django.utils.safestring import mark_safe
from rest_framework.authtoken.models import TokenProxy

from core.constants import RecipeConstants
from .models import (Tag,
                     Recipe,
                     Ingredient,
                     RecipeIngredient,
                     ShoppingCart,
                     TagRecipe)

admin.site.empty_value_display = RecipeConstants.ADMIN_EMPTY_VALUE


class BaseIngredientTagFormSet(models.BaseInlineFormSet):

    def is_valid(self):
        return super().is_valid() and not any(bool(e) for e in self.errors)

    def clean(self):
        count = sum(1 for form in self.forms if
                    form.cleaned_data and not form.cleaned_data.get('DELETE',
                                                                    False))
        if count < 1:
            raise ValidationError(
                'В рецепте должен быть хотя бы один {}.'.format(
                    self.model._meta.verbose_name))


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = RecipeConstants.MIN_VALUE
    formset = BaseIngredientTagFormSet


class TagRecipeInLine(admin.TabularInline):
    model = TagRecipe
    min_num = RecipeConstants.MIN_VALUE
    formset = BaseIngredientTagFormSet


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'author',
                    'get_favorites',
                    'get_ingredients',
                    'get_image')
    search_fields = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    inlines = (RecipeIngredientInline, TagRecipeInLine)

    @admin.display(description=RecipeConstants.FAVORITES_DESCRIPTION)
    def get_favorites(self, obj):
        return obj.favorites.count()

    @admin.display(description=RecipeConstants.IMAGE_DESCRIPTION)
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="60">')

    @admin.display(description=RecipeConstants.INGREDIENTS_DESCRIPTION)
    def get_ingredients(self, obj):
        return ', '.join([i.name for i in obj.ingredients.all()])


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe', 'ingredient')
    list_filter = ('recipe', 'ingredient')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')


admin.site.unregister(TokenProxy)
admin.site.unregister(Group)
