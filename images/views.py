import random
import tempfile
import traceback
import uuid
from datetime import datetime
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.files.storage import DefaultStorage
from django.core.files.temp import NamedTemporaryFile
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.parsers import JSONParser, FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from images.models import Image
from images.paginations import ImagesPagination
from images.serializer import ImageSerializer, ImageUploadSerializer

from PIL import Image as PilImg


# Create your views here.

class ImageAdmin(APIView):
    pagination_class = ImagesPagination
    def get(self, request):
        return JsonResponse(ImageSerializer(Image.objects.all(), many=True).data, safe=False)

class ImageView(APIView):

    def get(self, request, file_name, size=""):
        filter = Image.objects.filter(original_image=file_name)
        if not filter.exists():
            return JsonResponse({"message": "image_not_found"}, status=status.HTTP_404_NOT_FOUND)
        a = (filter.first())
        if size == "" or size == "original":
            print(dir(a.image_owner))

        return FileResponse(a.original_image.open(), content_type=a.image_type)


class ImageManage(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]
    serializer_class = [ImageUploadSerializer]

    def put(self, request):
        try:
            if len(request.FILES) > 0:
                image = request.FILES["image"]
                print(repr(image))
                type = "*"
                if image:
                    try:
                        img = PilImg.open(image)
                        type = img.format
                    except Exception as e:
                        print(e)
                        print(traceback.print_tb(e.__traceback__))
                        return JsonResponse({"message": "invalid_image"}, status=status.HTTP_400_BAD_REQUEST)
                    image_id = uuid.uuid1().hex
                    image._name = image_id
                    print(type)
                    img = Image(original_image=image, upload_date=timezone.now(), image_owner=request.user, image_type=f"image/{type.lower()}")
                    img.save()
                    return JsonResponse({"message": "success", "image_id": image_id})
            else:
                return JsonResponse({"message": "image_not_found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            print(traceback.print_tb(e.__traceback__))
            return JsonResponse({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
