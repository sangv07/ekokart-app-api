from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from . import serializers


# creating Re-Usable Baes Class for Tag and Ingredient
# we can create Baesclass and child class can inherit BaseClass
# look for Example TagViewSet (inheriting base class) and IngredientsViewSet (without BaseClass)
#
#
#
# """There are other methods in CBVs that interact with serializers.
#   For example, get_serializer() returns an already-instantiated serializer,
#   while get_serializer_context() returns the arguments you'll pass to the serializer
#       when creating its instance. For views that create or update data,
#   there are create and update that validate the data with the is_valid method to be saved,
#   and perform_create and perform_update that call the serializer's save method."""
#
class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.CreateModelMixin,
                            mixins.ListModelMixin):
    """Base viewset for user owned recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


    def perform_create(self, serializer):
        """Save objects into Database"""
        serializer.save(useraccount=self.request.user)


# We hare inheriting from Above BaseRecipeAttrViewSet(). it will inherit all attributes of those class (variable, methods).
class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""
    print('*****Tag_ViewSet*****')

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(useraccount=self.request.user).order_by('-tag_name')

    # perform_create will execute bcoz we inherit BaseClass()


class IngredientViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    """Manage ingredients in the database"""
    print('*****Ingredient_ViewSet*****')

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    # GET from Database
    def get_queryset(self):
        """return objects for the current authenticated user only"""
        return self.queryset.filter(useraccount=self.request.user).order_by('-ing_name')

    # '''create function is a function that allows us to hook into the create process when creating an object
    # and what happens is when we do a create object in our viewset this function will be invoked and the serializer the
    # validated sterilizer will be passed in as a serializer argument and then we can perform any modifications here that we'd like to create process'''
    # Create/POST
    def perform_create(self, serializer):
        """Create a new Ingredient"""
        serializer.save(useraccount=self.request.user)


# creating views function for Reverse' recipe-list' and 'recipe-detail'
class RecipeViewSet(viewsets.ModelViewSet):
    """Manage Recipe in the database"""
    print('*****Recipe_ViewSet*****')

    serializer_class = serializers.RecipeSerializer  # importing from recipe/serializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authentication user only"""
        return self.queryset.filter(useraccount=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(useraccount=self.request.user)
