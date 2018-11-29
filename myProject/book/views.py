from rest_framework import permissions, views, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from book.models import User, Book, Author, BookAuthor
from book.serializers import (UserSerializer,
                              BookSerializer,
                              RegistrationSerializer,
                              LoginSerializer,
                              AuthorSerializer,
                              BookAuthorSerializer)


class LogoutView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class RegistrationAPIView(views.APIView):
    """
    Registers a new user.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'token': serializer.data.get('token', None),
            },
            status=status.HTTP_201_CREATED,
        )


class ActionBasedPermission(permissions.AllowAny):
    """
    Grant or deny access to a view, based on a mapping in view.action_permissions
    """

    def has_permission(self, request, view):
        for klass, actions in getattr(view, 'action_permissions', {}).items():
            if view.action in actions:
                return klass().has_permission(request, view)
        return False


class UserModelViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    permission_classes = (ActionBasedPermission,)
    action_permissions = {
        permissions.IsAuthenticated: ['update', 'partial_update', 'delete'],
        permissions.IsAdminUser: ['list'],
        permissions.AllowAny: ['retrieve']
    }
    http_method_names = ['get', 'post', 'patch', 'delete']


class BookModelViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    http_method_names = ['get', 'post', 'patch', 'delete']


class AuthorModelViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    serializer_class = AuthorSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']


class BookAuthorViewSet(viewsets.ModelViewSet):
    queryset = BookAuthor.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    serializer_class = BookAuthorSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']


class LoginApiView(ObtainAuthToken):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
