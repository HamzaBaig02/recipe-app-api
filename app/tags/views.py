from rest_framework import mixins, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag
from tags import serializers


class TagViewSet(mixins.UpdateModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

