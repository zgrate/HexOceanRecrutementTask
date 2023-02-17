from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from tiers.models import Tier, ImageSize


# Create your tests here.

def create_tier(name, heights, can_access_original, can_generate_expiring):
    tier = Tier(tier_name=name, can_access_original=can_access_original,
                can_generate_expire_links=can_generate_expiring)
    tier.save()
    allowed_sizes = []
    for h in heights:
        allowed_sizes.append(ImageSize.objects.get_or_create(height=h)[0])
    tier.allowed_sizes.set(allowed_sizes)
    tier.save()


def create_default_tiers():
    ImageSize(height=200).save()
    ImageSize(height=400).save()
    create_tier("Basic", [200], False, False)
    create_tier("Premium", [200, 400], True, False)
    create_tier("Enterprise", [200, 400], True, True)


class TiersTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.test_user1 = User.objects.create_user("test", "test@test.pl", "password")
        self.test_user2 = User.objects.create_user("test2", "test2@test.pl", "password")
        create_default_tiers()

    def test_basic_tiers_existence(self):
        self.assertTrue(Tier.objects.filter(tier_name="Basic").exists())
        self.assertTrue(Tier.objects.filter(tier_name="Premium").exists())
        self.assertTrue(Tier.objects.filter(tier_name="Enterprise").exists())
