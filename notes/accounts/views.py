from urllib import request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .serializer import AuthSerializer ,UserListSerializer
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from accounts.models import CustomUser

class RegisterView(APIView):
    permission_classes = (AllowAny, )

    def post(self,request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


class LoginView(APIView):
    permission_classes = (AllowAny, )

    def post(self,request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response(
                {"detail": "email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = authenticate(
            request,
            email=email,
            password=password,
        )
        if user is None:
            return Response(
                "something went wrong please enter correct credential",
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(
            {"id": user.id, "email": user.email, "Role": user.Role},
            status=status.HTTP_200_OK,
        )
       
class UserView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        role = str(request.user.Role).lower()

        if role not in {"manager", "superadmin"}:
            return Response(status=status.HTTP_403_FORBIDDEN)

        users = CustomUser.objects.filter(Role="user")
        serializer = UserListSerializer(users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    


class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "email": user.email,
            "role": user.Role,
        })