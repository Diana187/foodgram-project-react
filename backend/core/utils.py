import base64


from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)

def check_and_delete_item(user, recipe, model_class, error_message):
    """Проверка наличия и удаления элемента для избранного и списка покупок."""
    if not model_class.objects.filter(user=user, recipe=recipe):
        return Response(
            {'errors': error_message},
            status=status.HTTP_400_BAD_REQUEST
        )
    model_class.objects.get(user=user, recipe=recipe).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)