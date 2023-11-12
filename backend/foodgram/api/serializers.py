from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.fields import IntegerField, CharField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Ingredient, Recipe, Tag, Favorite, RecipeIngredient

User = get_user_model()


class UserGetSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientGetSerializer(ModelSerializer):
    id = IntegerField(source='ingredient.id', read_only=True)
    name = CharField(source='ingredient.name', read_only=True)
    measurement_unit = CharField(source='ingredient.measurement_unit',
                                 read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientPostSerializer(ModelSerializer):
    id = IntegerField(source='ingredient.id')
    amount = IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(ModelSerializer):
    image = Base64ImageField(required=True)
    tags = TagSerializer(many=True, read_only=True)
    author = UserGetSerializer(read_only=True)
    is_in_shopping_cart = SerializerMethodField(
        method_name='_is_in_shopping_cart')
    is_favorited = SerializerMethodField(method_name='_is_favorited')
    ingredients = IngredientGetSerializer(many=True, read_only=True,
                                          source='recipeingredient')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def _is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def _is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shoppingcarts.filter(recipe=obj).exists()


class RecipePostSerializer(ModelSerializer):
    ingredients = IngredientPostSerializer(many=True,
                                           source='recipeingredients')
    tags = PrimaryKeyRelatedField(many=True,
                                  queryset=Tag.objects.all())
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time')

    def create(self, validated_data):
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=self.context.get('request'),
                                       **validated_data)
        recipe.tags.set(tags)
        ingredients_list = []
        for ingredient in ingredients:
            ingredients_list.append(RecipeIngredient(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient,
                                             pk=ingredient.get('pk')),
                amount=ingredient.get('amount')
            )
            )
        RecipeIngredient.objects.bulk_create(ingredients_list)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(instance).data


class FavoriteSerializer(ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже добавлен в избранное.'
            )
        ]
