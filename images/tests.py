import base64
import io
import json
from datetime import datetime
from io import BytesIO

from PIL import Image as PilImg
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient

from HexOceanTask import settings
from images.models import Image
from tiers.models import UserInTier, Tier
from tiers.tests import create_default_tiers


# Create your tests here.


def generate_base_64_basic_auth(username, password):
    return f"Basic {base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('utf-8')}"


def prepare_test_image():
    image_to_upload = PilImg.new("RGB", (256, 256), "red")
    bytes_obj = BytesIO()
    image_to_upload.save(bytes_obj, "JPEG")
    bytes_obj.seek(io.SEEK_SET)
    return SimpleUploadedFile("test.jpg", bytes_obj.read(), content_type="image/JPEG")


def create_test_users():
    User.objects.create_user("test", "test@test.pl", "password")
    User.objects.create_user("test2", "test2@test.pl", "password")


def put_image(username, password):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=generate_base_64_basic_auth(username, password))
    uploaded_photo = (client.put("/images/", {"image": prepare_test_image()}))
    assert uploaded_photo.status_code == 201
    return json.loads(uploaded_photo.content.decode())["image_id"]


FROZE_TIME = "2023-02-15 12:00"


class ImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        create_test_users()

    def test_upload_photo(self):
        image = prepare_test_image()

        self.client.credentials(HTTP_AUTHORIZATION=generate_base_64_basic_auth("test", "password"))
        response = (self.client.put("/images/", {"image": image}))
        content = json.loads(response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(content['detail'], "success")
        self.assertTrue(Image.objects.get(original_image=content["image_id"]))

    def test_upload_invalid(self):
        image = SimpleUploadedFile("test.jpg", b"This is not an image", content_type="image/JPEG")
        self.client.credentials(HTTP_AUTHORIZATION=generate_base_64_basic_auth("test", "password"))
        response = (self.client.put("/images/", {"image": image}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_with_no_login(self):
        image = prepare_test_image()
        response = (self.client.put("/images/", {"image": image}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_with_invalid_login(self):
        image = prepare_test_image()
        self.client.credentials(HTTP_AUTHORIZATION=generate_base_64_basic_auth("invalid", "password"))
        response = (self.client.put("/images/", {"image": image}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_with_no_image(self):
        self.client.credentials(HTTP_AUTHORIZATION=generate_base_64_basic_auth("test", "password"))
        response = (self.client.put("/images/"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class ImageViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        create_test_users()
        create_default_tiers()
        UserInTier(tier=Tier.objects.get(tier_name="Basic"), user=User.objects.get(username="test")).save()
        UserInTier(tier=Tier.objects.get(tier_name="Enterprise"), user=User.objects.get(username="test2")).save()
        self.test1_photo = put_image("test", "password")
        self.test2_photo = put_image("test2", "password")
        pass

    def test_download_original(self):
        response = (self.client.get("/images/" + self.test2_photo))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers['Content-Type'], "image/jpeg")
        self.assertTrue(response.readable)
        pass

    def test_download_original_error(self):
        response = (self.client.get("/images/non_existent_photo"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_download_original_should_no_permission(self):
        response = (self.client.get("/images/" + self.test1_photo))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_download_200_should_ok(self):
        response = self.client.get("/images/" + self.test1_photo + "/200")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_download_400_should_ok(self):
        response = self.client.get("/images/" + self.test2_photo + "/400")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_download_600_should_bad_request(self):
        response = self.client.get("/images/" + self.test2_photo + "/600")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



class ExpiringImageTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        create_test_users()
        create_default_tiers()
        UserInTier(tier=Tier.objects.get(tier_name="Enterprise"), user=User.objects.get(username="test2")).save()
        self.test1_photo = put_image("test", "password")
        self.test2_photo = put_image("test2", "password")
        pass

    @freeze_time(FROZE_TIME)
    def test_create_expiring_link(self):
        self.client.credentials(HTTP_AUTHORIZATION=generate_base_64_basic_auth("test2", "password"))
        response = self.client.post("/images/expire/",
                                    {"image_id": self.test2_photo, "expire_time": settings.MIN_EXPIRE_TIME})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content.decode())
        date = datetime.fromisoformat(content["expire_time"][:-1])
        frozen_time = (datetime.fromisoformat(FROZE_TIME))
        self.assertEqual((date - frozen_time).seconds, settings.MIN_EXPIRE_TIME)
        response = (self.client.get(content["expiry_link"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.headers['Content-Type'], "image/jpeg")

    def test_create_expiring_link_timeout_error(self):
        with freeze_time(FROZE_TIME) as frozen_datetime:
            self.client.credentials(HTTP_AUTHORIZATION=generate_base_64_basic_auth("test2", "password"))
            response = self.client.post("/images/expire/",
                                        {"image_id": self.test2_photo, "expire_time": settings.MIN_EXPIRE_TIME})
            content = json.loads(response.content.decode())
            response = (self.client.get(content["expiry_link"]))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            frozen_datetime.tick(settings.MIN_EXPIRE_TIME + 1)
            response = (self.client.get(content["expiry_link"]))
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_expiring_link_no_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=generate_base_64_basic_auth("test", "password"))
        response = self.client.post("/images/expire/",
                                    {"image_id": self.test1_photo, "expire_time": settings.MIN_EXPIRE_TIME})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_expiring_link_should_error_min_value(self):
        self.client.credentials(HTTP_AUTHORIZATION=generate_base_64_basic_auth("test2", "password"))
        response = self.client.post("/images/expire/",
                                    {"image_id": self.test2_photo, "expire_time": settings.MIN_EXPIRE_TIME - 100})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_expiring_link_should_error_max_value(self):
        self.client.credentials(HTTP_AUTHORIZATION=generate_base_64_basic_auth("test2", "password"))
        response = self.client.post("/images/expire/",
                                    {"image_id": self.test2_photo, "expire_time": settings.MAX_EXPIRE_TIME + 100})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

