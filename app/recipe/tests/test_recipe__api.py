from decimal import Decimal
import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
import tempfile
import os
from PIL import Image
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse("recipe:recipe-list")
# INGREDIENTS_URL = reverse("recipe:ingredient-list")


def detail_url(recipe_id):
    return reverse("recipe:recipe-detail", args=[recipe_id])

def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def create_recipe(user, **params):
    defaults = {
        "title": "Sample recipe",
        "time_minutes": 22,
        "price": Decimal("5.25"),
        "description": "Sample description",
        "link": "http://example.com/recipe.pdf",
    }

    defaults.update(params)

    tag1 = Tag.objects.create(name="Original Tag 1")
    tag2 = Tag.objects.create(name="Original Tag 2")
    ingredient1 = Ingredient.objects.create(name='Ingredient 1')
    ingredient2 = Ingredient.objects.create(name='Ingredient 2')
    recipe = Recipe.objects.create(user=user, **defaults)

    recipe.tags.add(tag1, tag2)
    recipe.ingredients.add(ingredient1,ingredient2)

    return recipe


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="user@example.com", password="test123")
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):

        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):

        other_user = create_user(email="otheruser@example.com", password="test123")

        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(serializer.data, res.data)

    def test_partial_update(self):

        original_link = "https://example.com/recipe.pdf"
        recipe = create_recipe(
            user=self.user, title="sample recipe title", link=original_link
        )

        payload = {"title": "New recipe title"}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        recipe = create_recipe(
            user=self.user,
            title="sample recipe title",
            link="https://example.com/recipe.pdf",
            description="Sample description",
        )

        payload = {
            "title": "Sample recipe",
            "description": "Sample description",
            "time_minutes": 10,
            "price": Decimal("2.50"),
            "link": "http://example.com/recipe.pdf",
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):

        new_user = create_user(email="testuser@examplpe.com", password="test123")
        recipe = create_recipe(user=self.user)

        payload = {"user": new_user.id}

        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        other_user = create_user(email="otheruser@example.com", password="test123")
        recipe = create_recipe(user=other_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_tags(self):

        payload = {
            "title": "Test Recipe Title",
            "time_minutes": 10,
            "price": "5.00",
            "link": "https://example.com/test-recipe",
            "tags": [{"name": "Test Tag 1"}, {"name": "Test Tag 2"}],
            "description": "This is a test recipe description for testing purposes.",
        }

        res = self.client.post(
            RECIPES_URL, data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        tag_count = Tag.objects.all().count()

        self.assertEqual(tag_count, 2)

    def test_update_recipe_with_tags(self):
        payload = {
            "tags": [{"name": "Updated Tag 1"}, {"name": "Updated Tag 2"}]
        }

        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)

        res = self.client.patch(url, data=json.dumps(payload), content_type='application/json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        tags = recipe.tags.all()

        tag_names = [tag.name for tag in tags]

        self.assertIn("Updated Tag 1", tag_names)
        self.assertIn("Updated Tag 2", tag_names)
        self.assertNotIn("Original Tag 1", tag_names)
        self.assertNotIn("Original Tag 2", tag_names)

        self.assertEqual(tags.count(), 2)

    def test_create_recipe_with_ingredients(self):
        payload = {
            "title": "Test Recipe Title",
            "time_minutes": 10,
            "price": "5.00",
            "link": "https://example.com/test-recipe",
            "tags": [{"name": "Test Tag 1"}, {"name": "Test Tag 2"}],
            "ingredients": [
                {"name": "Test Ingredient 1"},
                {"name": "Test Ingredient 2"},
            ],
            "description": "This is a test recipe description for testing purposes.",
        }

        res = self.client.post(
            RECIPES_URL, data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        ingredient_count = Ingredient.objects.all().count()

        self.assertEqual(ingredient_count, 2)


    def test_update_recipe_with_ingredients(self):

        recipe = create_recipe(user=self.user)

        payload = {
            "ingredients": [
                {"name": "Updated Ingredient 1"},
                {"name": "Updated Ingredient 2"}
            ]
        }

        url = detail_url(recipe.id)

        res = self.client.patch(url, data=json.dumps(payload), content_type='application/json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        ingredients = recipe.ingredients.all()
        ingredient_names = [ingredient.name for ingredient in ingredients]

        self.assertIn("Updated Ingredient 1", ingredient_names)
        self.assertIn("Updated Ingredient 2", ingredient_names)
        self.assertNotIn("Ingredient 1", ingredient_names)
        self.assertNotIn("Ingredient 2", ingredient_names)

        self.assertEqual(ingredients.count(), 2)


class ImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123'
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):

        url = image_upload_url(self.recipe.id)
        # Create a temporary file with a `.jpeg` extension
        with tempfile.NamedTemporaryFile(suffix='.jpeg') as image_file:

            # Create a new image with 'RGB' mode and size 10x10 pixels
            img = Image.new('RGB', (10, 10))

            # Save the image in the temporary file we created
            img.save(image_file)

            # Move the file pointer back to the beginning of the file
            # (necessary before reading or sending the file)
            image_file.seek(0)

            # Create a payload that contains the image file
            # 'image_file' is treated as a file object to be sent in a POST request
            payload = {'image': image_file}

            # Send a POST request with the image as part of a multipart/form-data payload
            # 'self.client.post()' is typically part of a test client in Django or a similar framework
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image',res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):

        url = image_upload_url(self.recipe.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)