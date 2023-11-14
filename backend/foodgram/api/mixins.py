from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response

User = get_user_model()
def _create_related_object(pk, request, serializer_class, author=False):
    if author:
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

def _delete_related_object(pk, request, model, author=False):
    try:
        if author:
            model.objects.filter(user=request.user, author=pk).delete()
        else:
            model.objects.filter(user=request.user, recipe=pk).delete()
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={'error': 'Запрашиваемый объект не найден.'})
    return Response(status=status.HTTP_204_NO_CONTENT)
