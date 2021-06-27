"""
creating a serializer for our create user request.
and the we will create view which will handle the request and we will wire views to URL
"""

from django.contrib.auth import get_user_model, authenticate
# In the Python code that are going to be output to the screen it's a good idea to pass them through this translation system just so if you ever do add any
# extra languages to your projects you can easily add the language file and it will automatically convert all of the text to the correct language.
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users objects"""
    print('*****User_Serializer*****')


    class Meta:
        # This method will return the currently active User model – the custom User model if one is specified, or User otherwise (in this case app/core/models/UserAccount())
        model = get_user_model()
        fields = ('email', 'password', 'username')  # fields that will be popup un REST-API Body
        extra_kwargs = {
            'password': {'write_only': True,
                         'min_length': 5}
        }


    # what Django rest framework does is when we're ready to create the user it
    # will call this create function and it will pass in the validated_data.
    # The validated_data will contain all of the data that was passed into our serializer
    # which would be the JSON data that was made in the HTTP POST
    # and it passes it as the argument here and then we can then use that to create our user.
    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


# creating Token API to make our unit tests pass again
class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user_authentication objects"""
    print('*****Auth_TokenSerializer*****')

    email = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'},
                                     trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            # '''so what this does is it raises the validation error and then the Django rest framework
            #     knows how to handle this error and it handles it by passing the error as a 400
            #     response and sending a response to the user which describes this message here
            # '''
            raise serializers.ValidationError(msg, code='authorization')

        '''now what we can do is we can set our user in the attributes which we return.
            So attrs user = user so then user will be set to the user object and then we can just return attrs
            so whenever you're overriding the validate function you must return the values at the end once the validation is
            successful.'''
        attrs['user'] = user
        return attrs
