from rest_framework import serializers

from core.models import Recipe, Tag
from tags.serializers import TagSerializer


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True,required=False)

    class Meta:
        model=Recipe
        fields = ['id','title','time_minutes','price','link', 'tags']
        read_only = ['id']

    def create(self, validated_data):
        # Pop the tags data from validated_data
        tags_data = validated_data.pop('tags', [])

        # Create the Recipe instance
        recipe = Recipe.objects.create(**validated_data)

        # Handle tag creation or get existing tags
        for tag_data in tags_data:
            tag_name = tag_data['name']
            tag, created = Tag.objects.get_or_create(name=tag_name)
            recipe.tags.add(tag)  # Add the tag to the recipe

        return recipe

    def update(self, instance, validated_data):
        # Handle updating the recipe including its tags
        tags_data = validated_data.pop('tags', None)

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

        return instance


class RecipeDetailSerializer(RecipeSerializer):

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
