from django.contrib import admin
from django.contrib.auth.models import Group
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


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = RecipeConstants.MIN_VALUE


class TagRecipeInLine(admin.TabularInline):
    model = TagRecipe
    min_num = RecipeConstants.MIN_VALUE


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
        return obj.is_favorited.count()

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
