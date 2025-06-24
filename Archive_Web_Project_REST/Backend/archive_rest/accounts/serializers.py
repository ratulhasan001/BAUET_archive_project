from rest_framework import serializers
from . import models
from django.contrib.auth.models import User

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = '__all__'

# class RegistrationSerializer(serializers.ModelSerializer):
#     confirm_password = serializers.CharField(required = True)
#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password']
    
#     def save(self):
#         username = self.validated_data['username']
#         first_name = self.validated_data['first_name']
#         last_name = self.validated_data['last_name']
#         email = self.validated_data['email']
#         password = self.validated_data['password']
#         password2 = self.validated_data['confirm_password']
        
#         if password != password2:
#             raise serializers.ValidationError({'error' : "Password Doesn't Mactched"})
#         if User.objects.filter(email=email).exists():
#             raise serializers.ValidationError({'error' : "Email Already exists"})
#         account = User(username = username, email=email, first_name = first_name, last_name = last_name)
#         account.set_password(password)
#         account.is_active = False
#         account.save()
#         return account
    

from .models import Profile
from .constants import DESIGNATION, DEPARTMENT
class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(required=True, write_only=True)
    designation = serializers.ChoiceField(choices=DESIGNATION, required=True)
    dept = serializers.ChoiceField(choices=DEPARTMENT, required=False, allow_null=True)
    contact_number = serializers.CharField(max_length=11, required=False, allow_null=True)
    address = serializers.CharField(max_length=200, required=False, allow_null=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'confirm_password',
            'designation',
            'dept',
            'contact_number',
            'address',
            'image',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):

        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'error': "Password Doesn't Match"})
        

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'error': "Email Already Exists"})

        return data

    def create(self, validated_data):

        designation = validated_data.pop('designation')
        dept = validated_data.pop('dept', None)
        contact_number = validated_data.pop('contact_number', None)
        address = validated_data.pop('address', None)
        image = validated_data.pop('image', None)


        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False 
        )


        Profile.objects.create(
            user=user,
            designation=designation,
            dept=dept,
            contact_number=contact_number,
            address=address,
            image=image
        )

        return user



class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required = True)
    password = serializers.CharField(required = True)