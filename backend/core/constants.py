"""Константы, используемые в приложениях."""


class RecipeConstants:
    """Константы для приложения рецептов."""

    ADMIN_EMPTY_VALUE = 'Не задано'
    FAVORITES_DESCRIPTION = 'В избранном'
    INGREDIENTS_DESCRIPTION = 'Ингредиенты'
    IMAGE_DESCRIPTION = 'Изображение'
    MAX_STR_LENGTH = 200
    TAG_COLOR_LENGTH = 7
    STR_RETURN_VALUE = 30
    RECIPE_TEXT_LENGTH = 10000
    COOKING_TIME_MAX_VALUE_VALIDATOR_VALUE = 50
    MAXIMUM_AMOUNT_REQUIRED = 300
    MIN_VALUE = 1


class UserConstants:
    """Константы для приложения пользователей."""

    USER_USERNAME_LENGTH = 150
    USER_EMAIL_LENGTH = 254
    USER_FIRST_NAME_LENGTH = 150
    USER_LAST_NAME_LENGTH = 150
    STR_RETURN_VALUE = 30
    RECIPES_AMOUNT = 'Количество рецептов'
    SUBSCRIBERS_AMOUNT = 'Количество подписчиков'


class APIConstants:
    """Константы для прилодения API."""

    API_MIN_VALUE = 1
    API_MAX_VALUE_INGREDIENTS = 50
    API_MAX_VALUE_COOKING_TIME = 360
    API_MIN_VALUE_ERROR_MESSAGE_INGREDIENTS = 'Минимальное значение: 1'
    API_MAX_VALUE_ERROR_MESSAGE_INGREDIENTS = 'Максимальное значение: 50'
    API_MAX_VALUE_ERROR_COOKING_TIME_MESSAGE = 'Максимальное значение: 360'
