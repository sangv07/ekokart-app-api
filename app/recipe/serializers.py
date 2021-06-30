from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe


# building serializers to convert complex data such as queryset and model instances to naitve python dataytpes
#   than can then be easily rendered into JSON, XML content types
class TagSerializer(serializers.ModelSerializer):   #
    """Serializer for tag object"""
    print('*****Tag_Serializer*****')

    class Meta:
        model = Tag
        fields = ('id', 'tag_name')
        read_only_fields = ('id',)

# the Django rest framework serializer is the normal serializer that will be used when building an API with Django. It simply parses data from complex types into JSON or XML.
# The model serializer is just the same as the above serializer in the sense that it does the same job, only that it builds the serializer based on the model, making the creation of the serializer easier than building it normally.
class IngredientSerializer(serializers.ModelSerializer):
    """Serializers for ingredients objects"""
    print('*****Ingredient_Serializer*****')

    class Meta:
        model = Ingredient
        fields = ('id','ing_name')
        read_only_fields = ('id',)


  # Serializing data from database or model
  # Django automatically includes all model fields in the serializer and creates the create and update methods.
class RecipeSerializer(serializers.ModelSerializer):
    """Serializers for Recipe objects"""
    print('*****Recipe_Serializer*****')

    # creating fields for ingredients and tags because these fields are not directly related to Recipe Model,
    # it is Foreign key from Ingredient and Tag model, Therefore; we are retrieving 'ID' of related Model(table)
    # PrimaryKeyRelatedField() means it return Primary_key field only (ID)
    ingredient_fk = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()  #  it simply lists the objects... the ingredients with their ID, with their primary key ID
    )
    tag_fk = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'time_minutes', 'price', 'link',
                  'ingredient_fk','tag_fk'  # we need to define the primary_key related filed for these two fields
                                        # because the 'ingredients','tags' are not part of the serializer, they are reference to the ingredient and tag model_class
                  )
        read_only_fields = ('id',)  # we are making 'id' read_only so that no body can change this

    # when calling RecipeSerializer() it wil return ==>> [OrderedDict([('id', 3), ('title', 'Chowmien'), ('time_minutes', 10), ('price', '7.00'), ('link', ''), ('ingredients', []), ('tags', [])] )]


# Inheriting from above as BaseSerializer
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer a recipe detail"""

    # we will inherit attributes from RecipeSerializer and override it.
    ingredient_fk = IngredientSerializer(many=True, read_only=True)
    tag_fk = TagSerializer(many=True, read_only=True)

    # since This class Inherit RecipeSerializer it will auto-inherit 'Class Meta:' too


# To handle the uploaded image (for this we are going to create View {get_serializer_class & upload_image()})
class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes"""

    class Meta:
        model = Recipe
        fields = ('id', 'image')
        read_only_fields = ('id',)
