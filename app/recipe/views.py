from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag

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
        """Create a new ingredient"""
        serializer.save(useraccount=self.request.user)
