import io
import logging
import uuid
from io import BytesIO

from PIL import Image as PilImg, UnidentifiedImageError
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse, FileResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from images.models import Image, ExpiringImage
from images.paginations import ImagesPagination
from images.serializer import ImageViewSerializer
from tiers.models import UserInTier


# Create your views here.

class   ImageAdmin(APIView):
    pagination_class = ImagesPagination
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tier = UserInTier.objects.get_or_create(user=request.user)[0].tier
        return JsonResponse(ImageViewSerializer(Image.objects.filter(image_owner__exact=request.user), many=True,
                                                context={"tier": tier}).data,
                            safe=False)

    def put(self, request):
        try:
            if len(request.FILES) > 0:
                image = request.FILES["image"]
                if image:
                    try:
                        img = PilImg.open(image)
                        image_type = img.format
                    except (UnidentifiedImageError, FileNotFoundError):
                        return JsonResponse({"detail": "invalid_image"}, status=status.HTTP_400_BAD_REQUEST)

                    image_id = uuid.uuid1().hex
                    image._name = image_id
                    img = Image(original_image=image, upload_date=timezone.now(), image_owner=request.user,
                                image_type=f"image/{image_type.lower()}")
                    img.save()
                    return JsonResponse({"detail": "success", "image_id": image_id}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({"detail": "image_not_found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Exception while processing the request", e)
            return JsonResponse({"detail": "internal_server_error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImageExpire(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    def post(self, request):

        tier = UserInTier.objects.get_or_create(user=request.user)[0].tier
        if not tier.can_generate_expire_links:
            return JsonResponse({"detail": "tier_too_low"}, status=status.HTTP_403_FORBIDDEN)

        if "image_id" not in request.data:
            return JsonResponse({"detail": "no_image_id"}, status=status.HTTP_400_BAD_REQUEST)
        image_id = request.data['image_id']
        img = Image.objects.filter(original_image=image_id, image_owner=request.user)
        if not img.exists():
            return JsonResponse({"detail": "image_not_found"}, status=status.HTTP_400_BAD_REQUEST)

        expire_time = settings.DEFAULT_EXPIRE_TIME
        if "expire_time" in request.data and request.data['expire_time']:
            expire_time = int(request.data['expire_time'])
            if expire_time < settings.MIN_EXPIRE_TIME:
                return JsonResponse({"detail": "expire_must_be_above", "value": settings.MIN_EXPIRE_TIME}, status=status.HTTP_400_BAD_REQUEST)
            if expire_time > settings.MAX_EXPIRE_TIME:
                return JsonResponse({"detail": "expire_must_be_below", "value": settings.MAX_EXPIRE_TIME}, status=status.HTTP_400_BAD_REQUEST)

        time_future = timezone.now() + timezone.timedelta(seconds=expire_time)

        expiry = ExpiringImage(image=img.first(), expiring_image_uuid=uuid.uuid1().hex, creation_date=timezone.now(),
                               expire_time=time_future)
        expiry.save()
        return JsonResponse({
            "expiry_link": reverse(f"img_view", args=[expiry.expiring_image_uuid], request=request),
            "expire_time": expiry.expire_time
        })


class ImageView(APIView):
    @method_decorator(cache_page(60 * 60 * 2))
    def get(self, request, file_name, size=""):
        filter = Image.objects.filter(original_image=file_name)
        expire_header = None
        if not filter.exists():
            expiring = ExpiringImage.find_delete_expiring_image(file_name)
            if not expiring:
                return JsonResponse({"detail": "image_not_found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                image = expiring.image
                expire_header = expiring.expire_time
        else:
            image = (filter.first())
        tier = UserInTier.objects.get_or_create(user=image.image_owner)[0].tier
        print(size)
        if size == "" or size == "original":
            if tier.can_access_original:
                return FileResponse(image.original_image.open(), content_type=image.image_type,
                                    headers={"Expire": expire_header})
            else:
                return JsonResponse({"detail": "tier_too_low"}, status=status.HTTP_403_FORBIDDEN)
        else:
            if not size.isdigit():
                return JsonResponse({"detail": "not_a_digit"})
            new_height = int(size)
            if not tier.allowed_sizes.filter(height=new_height).exists():
                return JsonResponse({"detail": "size_not_supported"}, status=status.HTTP_403_FORBIDDEN)

            temp_file = f"{image.original_image.name}_{new_height}"
            if not default_storage.exists("temp/" + temp_file):
                image.original_image.open()
                img = PilImg.open(image.original_image)
                new_width = int(img.width * (new_height / img.height))
                new_img = img.resize((new_width, new_height))
                out_file = BytesIO()
                new_img.save(out_file, "JPEG")
                out_file.seek(io.SEEK_SET)
                default_storage.save("temp/" + temp_file, out_file)

            return FileResponse(default_storage.open("temp/" + temp_file), content_type="image/jpeg")
