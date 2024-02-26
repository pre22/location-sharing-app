from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.decorators import permission_classes, api_view
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status, permissions
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomUser
from . import serializers

# Create your views here.
class UserLoginView(APIView):
    '''User Login View'''
    permission_classes = (permissions.AllowAny)

    def post(self, request, *args, **kwargs):
        serializer = serializers.UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            try:

                user = CustomUser.objects.get(phone=data["email"])
                check = user.check_password(data['password'])

                if check == True:
                    refresh_token = RefreshToken.for_user(user)
                    access_token = refresh_token.access_token
                    
                    response_data = {
                        'refresh_token': str(refresh_token), 
                        'access_token': str(access_token),
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'phone or password incorrect'}, status=status.HTTP_401_UNAUTHORIZED)

            except CustomUser.DoesNotExist:
                return Response(
                    {"message": "Invalid User, Kindly contact Support"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSignUpView(APIView):
    '''User Signup View'''
    permission_classes = (permissions.AllowAny)

    def post(self, request, *args, **kwargs):
        serializer = serializers.UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            try:
                # Check if email already exist
                user = CustomUser.objects.get(email=data['email'])
                if user:
                    response = {
                        'error': 'User with email already exist'
                    }
                    return Response(response, status=status.HTTP_200_OK)
                    
            except CustomUser.DoesNotExist:
                user = CustomUser.objects.create(email=data['email'], phone='234')
                user.is_active = True
                user.save()

                
                return Response(
                    {
                        'message': 'Registration Success. You can now login to your dashboard', 
                    },
                    status=status.HTTP_200_OK
                )


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
