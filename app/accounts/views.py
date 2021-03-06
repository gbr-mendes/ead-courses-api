from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializers import AuthTokenSerializer, UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a token for user"""
    serializer_class = AuthTokenSerializer
    permission_classes = (permissions.AllowAny,)
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManagerUserView(generics.RetrieveUpdateAPIView):
    """Retrive and update the user authenticated"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Get and return the authenticated user"""
        return self.request.user
