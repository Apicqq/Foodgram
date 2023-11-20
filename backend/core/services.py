from rest_framework import status
from rest_framework.response import Response

from recipes.models import RecipeIngredient


def pass_ingredients(ingredients, recipe):
    recipe_ingredients = [RecipeIngredient(
        recipe=recipe,
        ingredient=ingredient.get('id'),
        amount=ingredient.get('amount')
    ) for ingredient in ingredients]
    RecipeIngredient.objects.bulk_create(recipe_ingredients)


def prepare_ingredients_list(ingredients):
    shopping_list = []
    for item in ingredients:
        name = item.get('ingredient__name', 'Не указано')
        measurement_unit = (
            item.get('ingredient__measurement_unit', 'г.'))
        amount = item.get('ingredient_amount', 0)
        shopping_list.append(
            f'\n{name.capitalize()} - {amount}{measurement_unit}\n'
        )
    return ' '.join(shopping_list)


def _create_related_object(pk, request, serializer_class):
    serializer = serializer_class(
        data={
            'user': request.user.id,
            'recipe': pk},
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def _delete_related_object(pk, request, model):
    if not model.objects.filter(user=request.user, recipe=pk).exists():
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={'message': 'Запрашиваемый объект не найден'})
    model.objects.filter(user=request.user, recipe=pk).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
