from django.db import models


class UserRecipeBaseModel(models.Model):
    """Базовая модель для списков покупок и избранных рецептов."""

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        default_related_name = '%(class)ss'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s relation already exists.',
            )
        ]
        abstract = True
