from rest_framework import serializers

from core.models import Tag


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['id','name']
        read_only = ['id']