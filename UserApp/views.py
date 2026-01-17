from django.shortcuts import render,HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .serializers import RegisterSerializer, LoginSerializer
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
def index(request):
    return HttpResponse("User App is working!")


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        print("RegisterView.post called")
        print(f"Request data: {request.data}")
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully",
                    "user_id": user.id
                },
                status=status.HTTP_201_CREATED
            )
        print(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

