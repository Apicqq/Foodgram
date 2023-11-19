from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import OuterRef, Exists

from core.constants import RecipeConstants
from core.models import UserRecipeBaseModel


class RecipeQuerySet(models.QuerySet):
    def get_recipe_filters(self, user):
        return self.annotate(
            is_favorited=Exists(Favorite.objects.filter(
                user_id=user.id,
                recipe__id=OuterRef('pk')
            )),
            is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                user_id=user.id,
                recipe__id=OuterRef('pk')
            ))
        )


class Tag(models.Model, RecipeConstants):
    name = models.CharField(
        'Название тэга',
        max_length=RecipeConstants.MAX_STR_LENGTH,
        unique=True,
        help_text='Не более двухсот символов.'
    )
    color = ColorField(
        'Цвет тэга',
        unique=True,
        help_text='Цвет тэга в формате HEX, например: #FF0000.',
    )
    slug = models.SlugField(
        'Слаг',
        max_length=RecipeConstants.MAX_STR_LENGTH,
        unique=True,
        help_text='Транслитерированное название тэга.'
                  'Помимо латиницы доступен символ "-".',
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        default_related_name = '%(class)ss'

    def __str__(self):
        return self.name[:RecipeConstants.STR_RETURN_VALUE]


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Тэги',
        through='TagRecipe',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=RecipeConstants.MAX_STR_LENGTH,
    )
    text = models.CharField(
        'Описание рецепта',
        max_length=RecipeConstants.RECIPE_TEXT_LENGTH,
        # В ТЗ нет указания о длине текста, поставил примерное число.
        # Для чарфилда обязательно поставить какое-то.
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(
                RecipeConstants.MIN_VALUE,
                'Время приготовления должно быть '
                'не менее одной минуты.'
            ),
            MaxValueValidator(
                RecipeConstants.COOKING_TIME_MAX_VALUE_VALIDATOR_VALUE,
                'Время приготовления должно быть '
                'не более 360 минут.'
            )],
    )
    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)

    objects = RecipeQuerySet.as_manager()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = '%(class)ss'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:RecipeConstants.STR_RETURN_VALUE]


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=RecipeConstants.MAX_STR_LENGTH,
        help_text='Не более двухсот символов.'
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=RecipeConstants.MAX_STR_LENGTH,
        help_text='Не более двухсот символов.'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        default_related_name = '%(class)ss'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='%(app_label)s_%(class)s уже существует.',
            )
        ]

    def __str__(self):
        return self.name[:RecipeConstants.STR_RETURN_VALUE]


class Favorite(UserRecipeBaseModel):
    pass

    class Meta(UserRecipeBaseModel.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.name} в избранное.'


class ShoppingCart(UserRecipeBaseModel):
    pass

    class Meta(UserRecipeBaseModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return (f'{self.user.username} добавил'
                f' {self.recipe.name} в список покупок.')


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиентов',
        validators=[
            MinValueValidator(
                RecipeConstants.MIN_VALUE,
                'Количество ингредиентов должно быть'
                ' не менее одного.'
            ),
            MaxValueValidator(
                RecipeConstants.MAXIMUM_AMOUNT_REQUIRED,
                'Количество ингредиентов должно быть'
                ' не более 50.'
            ),
        ]
    )

    class Meta:
        default_related_name = '%(class)ss'
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return self.recipe.name[:RecipeConstants.STR_RETURN_VALUE]


class TagRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тэг',
    )

    class Meta:
        default_related_name = '%(class)ss'
        verbose_name = 'Тэг рецепта'
        verbose_name_plural = 'Тэги рецепта'

    def __str__(self):
        return self.tag.name[:RecipeConstants.STR_RETURN_VALUE]
