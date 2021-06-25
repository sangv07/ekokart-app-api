from rest_framework import serializers

from core.models import Tag , Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        model = Tag
        fields = ('id', 'username')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializers for ingredients objects"""

    class Meta:
        model = Ingredient
        fields = ('id','username')
        read_only_fields = ('id',)