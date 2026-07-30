from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import MeSerializer, RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="Register a student account")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=MeSerializer, summary="Return the authenticated user")
    def get(self, request):
        return Response(MeSerializer(request.user).data)
