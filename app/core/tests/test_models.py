
from decimal import Decimal
from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth import get_user_model

from core import models



class ModelTests(TestCase):

    def test_create_user_with_email_sucessful(self):
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))


    def test_new_user_email_normalized(self):

         sample_emails = [
             ['test1@EXAMPLE.com', 'test1@example.com'],
             ['Test2@Example.com', 'Test2@example.com'],
             ['test4@example.COM', 'test4@example.com']
         ]

         for email, expected in sample_emails:
             user = get_user_model().objects.create_user(email, 'sample123')
             self.assertEqual(user.email, expected)

    def test_new_user_without_email(self):

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('','test123')

    def test_create_super_user(self):

        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):

        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description'
        )

        self.assertEqual(str(recipe), recipe.title)


    def test_create_tag(self):

        tag = models.Tag.objects.create(
            name='Sample name'
        )

        self.assertEqual(str(tag),tag.name)


    def test_create_tag_with_recipe(self):

        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )

        tag1 = models.Tag.objects.create(
            name='Sample name'
        )

        tag2 = models.Tag.objects.create(
            name='Sample name2'
        )

        tag3 = models.Tag.objects.create(
            name='Sample name3'
        )


        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description'
        )

        recipe.tags.add(tag1,tag2,tag3)

        tags = recipe.tags.all()

        self.assertIn(tag1,tags)
        self.assertIn(tag2,tags)
        self.assertIn(tag3,tags)

    def test_create_ingredients_model(self):

        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description'
        )

        ingredient = models.Ingredient.objects.create(name='Sample Ingredient')
        ingredient2 = models.Ingredient.objects.create(name='Sample Ingredient2')

        self.assertEqual(str(ingredient),ingredient.name)

        recipe.ingredients.add(ingredient,ingredient2)

        ingredients = recipe.ingredients.all()

        self.assertIn(ingredient, ingredients)
        self.assertIn(ingredient2, ingredients)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')




