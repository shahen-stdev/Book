from django.contrib.auth import authenticate
from rest_framework import serializers

from book.models import Book, Author, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'birth_date', 'image')


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'birth_date', 'image')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('id', 'name', 'bio', 'date_of_birth')


class BookSerializer(serializers.ModelSerializer):
    # authors = serializers.PrimaryKeyRelatedField(many=True, queryset=Author.objects.all())
    authors = AuthorSerializer(many=True)
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Book
        fields = ('id', 'title', 'description', 'owner', 'authors')


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'password')

    def validate(self, attrs):
        username = attrs.get('email')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
