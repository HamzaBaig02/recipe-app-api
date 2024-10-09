from rest_framework import serializers

from core.models import Recipe
from tags.serializers import TagSerializer


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model=Recipe
        fields = ['id','title','time_minutes','price','link', 'tags']
        read_only = ['id']



class RecipeDetailSerializer(RecipeSerializer):

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
