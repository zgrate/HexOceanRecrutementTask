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


class ImageViewSerializer(serializers.BaseSerializer):
    def to_representation(self, instance: Image):
        tier = self.context["tier"]
        perma_links = {}
        if tier.can_access_original:
            perma_links["original"] = instance.original_image.url
        for size in tier.allowed_sizes.all():
            perma_links[f"size_{size.height}"] = f"{instance.original_image.url}/{size.height}"
        return {
            "upload_date": instance.upload_date,
            "image_id": instance.original_image.name,
            "perma_links": perma_links
        }
