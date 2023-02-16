from rest_framework import serializers
from rest_framework.fields import FileField
from rest_framework.serializers import Serializer

from images.models import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class ImageUploadSerializer(Serializer):
    file = FileField()
