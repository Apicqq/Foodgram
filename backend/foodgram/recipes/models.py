from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from core.models import BaseUserRecipeModel

User = get_user_model()
class Tag(models.Model):
    name = models.CharField(
        'Название тэга',
        max_length=200,
        unique=True,
        blank=False,
        null=False
    )
    color = models.CharField(
        'Цвет тэга',
        max_length=7,
        unique=True,
        blank=False,
        null=False
    )
    slug = models.SlugField(
        'Слаг',
        max_length=200,
        unique=True,
        blank=False,
        null=False,
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
        return self.name[:30]


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
        max_length=200,
        blank=False,
        null=False
    )
    text = models.CharField(
        'Описание рецепта',
        max_length=30000,
        blank=False,
        null=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        blank=False,
        null=False,
        validators=[
            MinValueValidator(
                1, 'Время приготовления должно быть '
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
        return self.name[:30]


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
    )
    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        default_related_name = '%(class)ss'

    def __str__(self):
        return self.name[:50]


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
                name='%(app_label)s_%(class) recipe has been marked'
                     'as favorite already.',
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
                name='\n%(app_label)s_%(class)s ingredient already added.',
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