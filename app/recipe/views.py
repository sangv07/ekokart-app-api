from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework import viewsets, mixins, status

from rest_framework.decorators import action, api_view  # to use add custom actions to views function()

from core.models import Tag, Ingredient, Recipe

from . import serializers


# Creating below mothod to handle RecipeImageSerializer class
def get_serializer_class(self):
    """Return appropriate serializer class"""
    if self.action == 'retrieve':
        return serializers.RecipeDetailSerializer
    elif self.action == 'upload_image':
        return serializers.RecipeImageSerializer

    return self.serializer_class


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

        # Implement feature for filtering tags
        # The reason we pass it in as an integer first is because our assigned only
        # Value is going to be a zero or a one they're going to be the supported values for assigned only and in
        # With the query parameters, there's no concept of type So if you type one in the parameter
        # then there's no way for it to know whether that was intended to be a string or whether it was intended to be a
        # Integer because you don't put quotes around them when you do query parameters get parameters
        # So what we need to do is first convert that to an integer and then convert to a boolean
        # otherwise if you do boolean of a string with zero in it
        assigned_only = bool(int(self.request.query_params.get('assigned_only', 0)))
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(useraccount=self.request.user).order_by('-tag_name').distinct()

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
        """return all objects for the current authenticated user only"""

        # Implement feature for filtering ingredients
        assigned_only = bool(int(self.request.query_params.get('assigned_only', 0)))
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(useraccount=self.request.user).order_by('-ing_name').distinct()

    # '''create function is a function that allows us to hook into the create process when creating an object
    # and what happens is when we do a create object in our viewset this function will be invoked and the serializer the
    # validated sterilizer will be passed in as a serializer argument and then we can perform any modifications here that we'd like to create process'''
    # Create/POST
    def perform_create(self, serializer):
        """Create a new Ingredient fpr logged in user"""
        serializer.save(useraccount=self.request.user)


# creating views function for Reverse' recipe-list' and 'recipe-detail'
class RecipeViewSet(viewsets.ModelViewSet):
    """Manage Recipe in the database"""
    print('*****Recipe_ViewSet*****')

    serializer_class = serializers.RecipeSerializer  # importing from recipe/serializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # creating private function to convert Str(queryset) to integer(id)
    def _params_to_ints(self, qryset):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qryset.split(',')]

    # Trigger PostMan GET{{url}}/api/recipe/recipes/
    def get_queryset(self):
        """Return objects for the current authentication user only"""
        print('*****RVS_get_querysert*****')

        # feature to filter recipes if they are provided a get parameters
        # if we have provided tags as a query param or a query string then it will
        # be assigned to tags the actual string that you provided and if not then by
        # default the get function returns none so the tags key doesn't exist in our query params
        tag_fk = self.request.query_params.get('tag_fk')
        ingredient_fk = self.request.query_params.get('ingredient_fk')
        queryset = self.queryset
        # please look above private _param_to_int function()
        if tag_fk:  # if tag_fk is not None:
            tag_ids = self._params_to_ints(tag_fk)
            # __id__in means filter by id in foreign_key and return all of the tags where the ID is in the list that we provided
            queryset = queryset.filter(tag_fk__id__in=tag_ids)
        if ingredient_fk:
            ingredient_ids = self._params_to_ints(ingredient_fk)
            queryset = queryset.filter(ingredient_fk__id__in=ingredient_ids)

        return queryset.filter(useraccount=self.request.user)

    # way the Django rest framework knows which serializer to display in the browse-able api
    #   So what we will do is we will check if the action is 'retrieve' or 'upload-image'
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        print('*****RVS_get_serializer_class*****')

        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    # trigger PostMan POST{{url}}/api/recipe/recipes/
    def perform_create(self, serializer):
        """Create a new recipe"""
        print('*****RVS_perform_create*****')

        serializer.save(useraccount=self.request.user)

    # using 'action' decorator (Method='to allow user to post image for recipe'
    # detail=True ==>> action will be specific detailed recipe with us already exist and able to use detail URL that has the ID or the Recipe in the URL
    # url_path = 'upload-image' ==>> this is path that will be visible in out URL-PATH
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
