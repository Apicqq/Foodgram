from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework.serializers import ModelSerializer

from recipes.models import Ingredient

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


class RecipeSerializer(ModelSerializer):
    pass