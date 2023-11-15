from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from core.constants import UserConstants
from .validators import validate_username


class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=UserConstants.USER_USERNAME_LENGTH,
        unique=True,
        blank=False,
        null=False,
        validators=(
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Имя пользователя содержит недопустимые символы.',
            ),
            validate_username
        )
        )
    email = models.EmailField(
        max_length=UserConstants.USER_EMAIL_LENGTH,
        unique=True,
        verbose_name='Адрес электронной почты',
        help_text='Адрес электронной почты',
        error_messages={
            'unique': 'Пользователь с таким адресом'
                      ' электронной почты уже существует.',
        }
    )
    first_name = models.CharField(
        max_length=UserConstants.USER_FIRST_NAME_LENGTH,
        verbose_name='Имя',
        help_text='Имя',
    )
    last_name = models.CharField(
        max_length=UserConstants.USER_LAST_NAME_LENGTH,
        verbose_name='Фамилия',
        help_text='Фамилия',
    )
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        default_related_name = '%(class)ss'
        ordering = ('username',)

    def __str__(self):
        return self.username[:UserConstants.STR_RETURN_VALUE]


class Subscription(models.Model):
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author',
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_prevent_self_follow',
                check=~models.Q(user=models.F('author')),
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}.'