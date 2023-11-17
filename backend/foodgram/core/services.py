from django.db.models import Sum
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from recipes.models import Ingredient, RecipeIngredient


def pass_ingredients(ingredients, recipe):
    recipe_ingredients = [RecipeIngredient(
        recipe=recipe,
        ingredient=get_object_or_404(Ingredient, pk=ingredient.get('id')),
        amount=ingredient.get('amount')
    ) for ingredient in ingredients]
    RecipeIngredient.objects.bulk_create(recipe_ingredients)
    return


def get_subscription_ingredients(request):
    shopping_list = []
    ingredients = (
        request.user.shoppingcarts.values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit'
        )
        .annotate(
            ingredient_amount=Sum(
                'recipe__recipeingredients__amount'
            )
        )
    )
    for item in ingredients:
        name = item.get('recipe__ingredients__name', 'Не указано')
        measurement_unit = (
            item.get('recipe__ingredients__measurement_unit', 'г.'))
        amount = item.get('ingredient_amount', 0)
        shopping_list.append(
            f'\n{name.capitalize()} - {amount}{measurement_unit}\n'
        )
    return ' '.join(shopping_list)


def _create_related_object(pk,
                           request,
                           serializer_class,
                           subscription_arg=False
                           ):
    if subscription_arg:
        serializer = serializer_class(
            data={
                'user': request.user.id,
                'author': pk},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
    else:
        serializer = serializer_class(
            data={
                'user': request.user.id,
                'recipe': pk},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def _delete_related_object(pk, request, model, subscription_arg=False):
    try:
        if subscription_arg:
            model.objects.filter(user=request.user, author=pk).delete()
        else:
            model.objects.filter(user=request.user, recipe=pk).delete()
    except model.ObjectDoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={'error': 'Запрашиваемый объект не найден.'})
    return Response(status=status.HTTP_204_NO_CONTENT)
