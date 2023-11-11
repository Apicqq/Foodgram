from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.fields import IntegerField, CharField
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from recipes.models import Ingredient, Recipe, Tag, Favorite, ShoppingCart, \
    RecipeIngredient

User = get_user_model()


class UserSignUpSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'first_name', 'last_name'
        )


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
    amount = IntegerField(source='amount')

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
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def _is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=request.user,
                                           recipe=obj).exists()


class RecipePostSerializer(ModelSerializer):
    ingredients = IngredientPostSerializer(many=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time')

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
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
