from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient

from recipe import serializers


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """Manage tags in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    # GET
    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(useraccount=self.request.user).order_by('-username')

    # '''create function is a function that allows us to hook into the create process when creating an object
        # and what happens is when we do a create object in our viewset this function will be invoked and the serializer the
        # validated sterilizer will be passed in as a serializer argument and then we can perform any modifications here that we'd like to create process'''
    # Create/POST
    def perform_create(self, serializer):
        """Create a new Tag"""
        serializer.save(useraccount=self.request.user)


class IngredientViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    """Manage ingredients in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    def get_queryset(self):
        """return objects for the current authenticated user only"""
        return self.queryset.filter(useraccount=self.request.user).order_by('-username')

    def perform_create(self, serializer):
        """Create a new Ingredient"""
        serializer.save(useraccount=self.request.user)