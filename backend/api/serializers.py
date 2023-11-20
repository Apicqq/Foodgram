from django.core.validators import MinValueValidator, MaxValueValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, IntegerField, ReadOnlyField, \
    BooleanField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator

from core.constants import APIConstants
from core.services import pass_ingredients
from recipes.models import (
    Ingredient,
    Favorite,
    Recipe,
    RecipeIngredient,
    Tag,
    ShoppingCart
)
from users.models import Subscription, User


class UserGetSerializer(ModelSerializer):
    """ Сериализатор для получения данных о пользователе."""

    is_subscribed = SerializerMethodField(method_name='_is_subscribed')

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed')
        read_only_fields = ('is_subscribed',)

    def _is_subscribed(self, obj):
        request = self.context.get('request')

        return (request
                and request.user.is_authenticated
                and request.user.follower.filter(author=obj).exists())


class IngredientSerializer(ModelSerializer):
    """ Сериализатор для работы с ингредиентами."""

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class TagSerializer(ModelSerializer):
    """ Сериализатор для работы с тегами."""

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientGetSerializer(ModelSerializer):
    """ Сериализатор для получения информации об ингредиентах в
    GET-запросах."""

    id = IntegerField(read_only=True, source='ingredient.id')
    name = CharField(source='ingredient.name', read_only=True)
    measurement_unit = CharField(source='ingredient.measurement_unit',
                                 read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientPostSerializer(ModelSerializer):
    """ Сериализатор для работы с ингредиентами в POST-запросах."""

    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField(validators=[
        MinValueValidator(
            APIConstants.API_MIN_VALUE,
            APIConstants.API_MIN_VALUE_ERROR_MESSAGE_INGREDIENTS
        ),
        MaxValueValidator(
            APIConstants.API_MAX_VALUE_INGREDIENTS,
            APIConstants.API_MAX_VALUE_ERROR_MESSAGE_INGREDIENTS
        ),
    ])

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(ModelSerializer):
    """ Сериализатор для работы с рецептами в GET-запросах."""

    image = Base64ImageField(required=True)
    tags = TagSerializer(many=True, read_only=True)
    author = UserGetSerializer()
    is_in_shopping_cart = BooleanField(default=0)
    is_favorited = BooleanField(default=0)
    ingredients = IngredientGetSerializer(many=True, read_only=True,
                                          source='recipeingredients')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_in_shopping_cart', 'is_favorited',
                  'name', 'image', 'text', 'cooking_time')


class RecipePostSerializer(ModelSerializer):
    """ Сериализатор для работы с рецептами в POST-запросах."""

    ingredients = IngredientPostSerializer(many=True)
    tags = PrimaryKeyRelatedField(many=True,
                                  queryset=Tag.objects.all())
    image = Base64ImageField(required=True)
    cooking_time = IntegerField(validators=[
        MinValueValidator(
            APIConstants.API_MIN_VALUE,
            APIConstants.API_MIN_VALUE_ERROR_MESSAGE_INGREDIENTS),
        MaxValueValidator(
            APIConstants.API_MAX_VALUE_COOKING_TIME,
            APIConstants.API_MAX_VALUE_ERROR_COOKING_TIME_MESSAGE),
    ])

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time')

    def validate(self, data):
        ingredients_list, tags_list = (
            [ingredient.get('id') for ingredient in data.get('ingredients')],
            [tag for tag in data.get('tags')]
        )
        if not ingredients_list or not tags_list:
            raise ValidationError('Вы не добавили ингредиенты '
                                  'и/или тэги.')
        if (len(set(ingredients_list)) != len(ingredients_list)
                or len(set(tags_list)) != len(tags_list)):
            raise ValidationError(
                'Проверьте корректность данных. В вашем запросе есть'
                ' дубликаты ингредиентов и/или тэгов.'
            )
        return data

    def validate_image(self, obj):
        if not obj:
            raise ValidationError('Добавьте изображение.')
        return obj

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=self.context.get('request').user,
                                       **validated_data)
        recipe.tags.set(tags)
        pass_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        pass_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeGetSerializer(instance,
                                   context=self.context).data


class FavoriteCartsBaseSerializer(ModelSerializer):
    unique_together = ('user', 'recipe')

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe,
            context=self.context
        ).data

    def validate(self, data):
        if self.Meta.model.objects.filter(
                user=self.context.get('request').user,
                recipe=data.get('recipe')).exists():
            raise ValidationError('Такая связь уже существует.')
        return data

    class Meta:
        fields = ('recipe', 'user')


class FavoriteSerializer(FavoriteCartsBaseSerializer):
    """ Сериализатор для работы с избранными рецептами."""

    class Meta(FavoriteCartsBaseSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(FavoriteCartsBaseSerializer):
    """ Сериализатор для работы со списком покупок."""

    class Meta(FavoriteCartsBaseSerializer.Meta):
        model = ShoppingCart


class RecipeMinifiedSerializer(ModelSerializer):
    """ Уменьшенная версия сериализатора списка рецептов.
    Используется при взаимодействии со списком покупок."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)


class SubscriptionsListSerializer(UserGetSerializer):
    """Сериализатор для работы со списком подписок."""

    recipes = SerializerMethodField(method_name='_recipes')
    recipes_count = ReadOnlyField(source='recipes.count')

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('__all__',)

    def _recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit and recipes_limit.isnumeric():
            recipes = recipes[:int(recipes_limit)]
        return RecipeMinifiedSerializer(recipes, many=True,
                                        context=self.context).data


class GetRemoveSubscriptionSerializer(ModelSerializer):
    """Добавление и удаление подписок пользователей."""

    class Meta:
        model = Subscription
        fields = ('author', 'user')
        read_only_fields = ('__all__',)

        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого автора.'
            )
        ]

    def to_representation(self, instance):
        return SubscriptionsListSerializer(instance.author,
                                           context=self.context).data

    def validate_author(self, obj):
        if obj == self.context.get('request').user:
            raise ValidationError('Нельзя подписаться на себя.')
        return obj
