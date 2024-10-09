from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag
from tags.serializers import TagSerializer

TAGS_URL = reverse("tags:tag-list")


def detail_url(tag_id):
    return reverse("tags:tag-detail", args=[tag_id])


def create_recipe(user, **params):
    defaults = {
        "title": "Sample recipe",
        "time_minutes": 22,
        "price": Decimal("5.25"),
        "description": "Sample description",
        "link": "http://example.com/recipe.pdf",
    }

    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicTagsAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="user@example.com", password="test123")
        self.client.force_authenticate(self.user)


    def test_retrieve_tags(self):

        tag1 = Tag.objects.create(name="Sample Tag")
        tag2 = Tag.objects.create(name="Sample Tag2")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_create_tag(self):

        payload = {"name": "Sample Tag"}

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        tag = Tag.objects.first()

        self.assertEqual(tag.id, res.data["id"])



