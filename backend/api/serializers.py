from django.db.transaction import atomic
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import (CharField,
                                   IntegerField,
                                   ReadOnlyField,
                                   BooleanField)
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator

from core.constants import RecipeConstants
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
    amount = IntegerField(
        min_value=RecipeConstants.MIN_VALUE,
        max_value=RecipeConstants.MAXIMUM_AMOUNT_ALLOWED,
        error_messages={
            'min_value': f'Убедитесь, что значение больше либо'
                         f' равно {RecipeConstants.MIN_VALUE}',
            'max_value': f'Убедитесь, что значение меньше либо'
                         f' равно {RecipeConstants.MAXIMUM_AMOUNT_ALLOWED}',
        }
    )

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
    cooking_time = IntegerField(
        min_value=RecipeConstants.MIN_VALUE,
        max_value=RecipeConstants.MAXIMUM_AMOUNT_ALLOWED,
        error_messages={
            'min_value': f'Убедитесь, что значение больше либо'
                         f' равно {RecipeConstants.MIN_VALUE}',
            'max_value': f'Убедитесь, что значение меньше либо'
                         f' равно {RecipeConstants.MAX_COOKING_TIME}',
        }
    )

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time')

    def validate(self, data):
        tags = data.get('tags')
        if not data.get('ingredients'):
            raise ValidationError(
                {'ingredients': 'Вы не добавили ингредиенты в рецепт.'}
            )
        ingredients_list = (
            [ingredient.get('id') for ingredient in data.get('ingredients')]
        )
        if not tags:
            raise ValidationError(
                {'tags': 'Вы не добавили тэги в рецепт.'}
            )
        if len(set(ingredients_list)) != len(ingredients_list):
            raise ValidationError(
                {'ingredients': 'Проверьте корректность данных. В вашем'
                                ' запросе есть дубликаты ингредиентов.'}
            )
        if len(set(tags)) != len(tags):
            raise ValidationError(
                {'tags': 'Проверьте корректность данных. В вашем'
                         ' запросе есть дубликаты тэгов.'}
            )
        return data

    def validate_image(self, obj):
        if not obj:
            raise ValidationError('Добавьте изображение.')
        return obj

    @atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=self.context.get('request').user,
                                       **validated_data)
        recipe.tags.set(tags)
        pass_ingredients(ingredients, recipe)
        return recipe

    @atomic
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
    class Meta:
        fields = ('recipe', 'user')

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe,
            context=self.context
        ).data

    def validate(self, data):
        if self.Meta.model.objects.filter(
                user=self.context.get('request').user,
                recipe=data.get('recipe')).exists():
            raise ValidationError(
                f'Вы уже добавили этот рецепт в'
                f' {self.Meta.model._meta.verbose_name.lower()}'
            )
        return data


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
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                pass
        return RecipeMinifiedSerializer(recipes, many=True,
                                        context=self.context).data


class GetRemoveSubscriptionSerializer(ModelSerializer):
    """Добавление и удаление подписок пользователей."""

    class Meta:
        model = Subscription
        fields = ('author', 'user')

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
