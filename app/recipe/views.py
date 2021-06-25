from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient

from recipe import serializers


# creating Re-Usable Baes Class for Tag and Ingredient
# we can create Baesclass and child class can inherit BaseClass
# look for Example TagViewSet (inheriting base class) and IngredientsViewSet (without BaseClass)
class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.CreateModelMixin,
                            mixins.ListModelMixin):
    """Base viewset for user owned recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(useraccount=self.request.user).order_by('-username')

    def perform_create(self, serializer):
        """Save objects into Database"""
        serializer.save(useraccount=self.request.user)


# We hare inheriting from Above BaseRecipeAttrViewSet(). it will inherit all attributes of those class (variable, methods).
class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    # get_queryset and perform_create will execute bcoz we inherit BaseClass()


class IngredientViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    """Manage ingredients in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    # GET from Database
    def get_queryset(self):
        """return objects for the current authenticated user only"""
        return self.queryset.filter(useraccount=self.request.user).order_by('-username')

    # '''create function is a function that allows us to hook into the create process when creating an object
    # and what happens is when we do a create object in our viewset this function will be invoked and the serializer the
    # validated sterilizer will be passed in as a serializer argument and then we can perform any modifications here that we'd like to create process'''
    # Create/POST
    def perform_create(self, serializer):
        """Create a new Ingredient"""
        serializer.save(useraccount=self.request.user)