from django.contrib.auth import get_user_model
from django.db import models

from recipes.models import Recipe

User = get_user_model()

class BaseUserRecipeModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        default_related_name = '%(class)ss'
        abstract = True