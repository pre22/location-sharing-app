from django.core.exceptions import ValidationError
from rest_framework import serializers



class UserRegistrationSerializer(serializers.Serializer):
    '''Handles User Registration'''
    email =  serializers.EmailField(required=True)
    password = serializers.CharField(max_length=50, required=True)
    confirm_password = serializers.CharField(max_length=50, required=True)

    def validate(self, attrs):
        password1 = attrs['password']
        password2 = attrs['confirm_password']

        if password1 != password2:
            data = {
                'error': 'Passwords does not match'
            }
        
            raise ValidationError(data)
        return attrs


class UserLoginSerializer(serializers.Serializer):
    '''Handles User Login'''
    email =  serializers.EmailField(required=True)
    password = serializers.CharField(max_length=50, required=True)



