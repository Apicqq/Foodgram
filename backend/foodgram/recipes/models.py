from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from core.constants import RecipeConstants

User = get_user_model()


class Tag(models.Model, RecipeConstants):
    name = models.CharField(
        'Название тэга',
        max_length=RecipeConstants.TAG_NAME_LENGTH,
        unique=True,
        blank=False,
        null=False,
        help_text='Не более двухсот символов.'
    )
    color = models.CharField(
        'Цвет тэга',
        max_length=RecipeConstants.TAG_COLOR_LENGTH,
        unique=True,
        blank=False,
        null=False,
        help_text='Цвет тэга в формате HEX, например: #FF0000.',
    )
    slug = models.SlugField(
        'Слаг',
        max_length=RecipeConstants.TAG_SLUG_LENGTH,
        unique=True,
        blank=False,
        null=False,
        help_text='Транслитерированное название тэга.'
                  'Помимо латиницы доступен символ "-".',
        validators=[
            RegexValidator(
                regex=r'[\w-]+$',
                message='Слаг содержит недопустимые символы.'

            )
        ]
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
        blank=True
    )
    name = models.CharField(
        'Название рецепта',
        max_length=RecipeConstants.RECIPE_NAME_LENGTH,
        blank=False,
        null=False
    )
    text = models.CharField(
        'Описание рецепта',
        max_length=RecipeConstants.RECIPE_TEXT_LENGTH,
        blank=False,
        null=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        blank=False,
        null=False,
        validators=[
            MinValueValidator(
                RecipeConstants.COOKING_TIME_MIN_VALUE_VALIDATOR_VALUE,
                'Время приготовления должно быть '
                'не менее одной минуты.'
            )],
    )
    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)

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
        max_length=RecipeConstants.INGREDIENT_NAME_LENGTH,
        help_text='Не более двухсот символов.'
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=RecipeConstants.INGREDIENT_MEAUSEREMENT_UNIT_LENGTH,
        help_text='Не более двухсот символов.'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        default_related_name = '%(class)ss'

    def __str__(self):
        return self.name[:RecipeConstants.STR_RETURN_VALUE]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='in_favorites'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s уже добавлен в избранное.',
            )
        ]

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.name} в избранное.'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shoppingcarts',
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='carts'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='\n%(app_label)s_%(class)s уже добавлен в список покупок.',
            )
        ]

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
                1, 'Количество ингредиентов должно быть'
                   ' не менее одного.'
            )
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
