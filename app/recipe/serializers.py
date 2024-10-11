from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient
from tags.serializers import TagSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['name']
        read_only = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True,required=False)
    ingredients = IngredientSerializer(many=True,required=False)

    class Meta:
        model=Recipe
        fields = ['id','title','time_minutes','price','link', 'tags', 'ingredients']
        read_only = ['id']

    def create(self, validated_data):
        # Pop the tags data from validated_data
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients',[])

        # Create the Recipe instance
        recipe = Recipe.objects.create(**validated_data)

        # Handle tag creation or get existing tags
        for tag_data in tags_data:
            tag_name = tag_data['name']
            tag, created = Tag.objects.get_or_create(name=tag_name)
            recipe.tags.add(tag)  # Add the tag to the recipe

        for ingredient_data in ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(name=ingredient_data['name'])
            recipe.ingredients.add(ingredient)

        return recipe


    def update(self, instance, validated_data):
        # Handle updating the recipe including its tags
        tags_data = validated_data.pop('tags', None)
        ingredients_data = validated_data.pop('ingredients',None)

        # Update the basic recipe fields
        for attr,value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # If tags are provided, update the tags
        if tags_data:
            instance.tags.clear()  # Clear existing tags
            for tag_data in tags_data:
                tag, created = Tag.objects.get_or_create(name=tag_data['name'])
                instance.tags.add(tag)

        if ingredients_data:
            instance.ingredients.clear()
            for ingredient_data in ingredients_data:
                ingredient, created = Ingredient.objects.get_or_create(name=ingredient_data['name'])
                instance.ingredients.add(ingredient)



        return instance


class RecipeDetailSerializer(RecipeSerializer):

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']


