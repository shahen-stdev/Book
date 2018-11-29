from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers

from book.models import Book, Author, User, BookAuthor


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


class BookAuthorSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    id = serializers.ReadOnlyField()

    class Meta:
        model = BookAuthor
        fields = ('id', 'author', 'book')


class CurrentUserField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        queryset = User.objects.filter(id=user.id)
        return queryset


class BookSerializer(serializers.ModelSerializer):
    owner = CurrentUserField()

    class Meta:
        model = Book
        fields = ('id', 'title', 'description', 'owner')
        depth = 1


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
