from rest_framework import serializers
from authentication.models import Account
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

    class Meta:
        model = Account
        fields = ('email', 'password', 'username','name')
        extra_kwargs = {
            "name": {"required": False, "allow_null": False},
            }

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError(
                self.default_error_messages)
        return attrs

    def create(self, validated_data):
        user = Account.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    username = serializers.CharField(default=None)
    name = serializers.CharField(default=None)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True, default=None)
    tokens = serializers.SerializerMethodField()
    login_count = serializers.IntegerField(default=0)
    country_code = serializers.CharField(default="",max_length=4)

    def get_tokens(self, obj):
        user = Account.objects.get(email=obj['email'])

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    class Meta:
        model = Account
        fields = ['email', 'password', 'username', 'tokens','name','login_count','country_code']
    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        filtered_user_by_email = Account.objects.filter(email=email)
        user = authenticate(email=email, password=password)
        
        if filtered_user_by_email.exists() and filtered_user_by_email[0].auth_provider != 'email':
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')

        return {
            'email': user.email,
            'username': user.username,
            'name':user.name,
            'login_count':user.login_count,
            'country_code':user.country_code,
            'tokens': user.tokens
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields='__all__'
        extra_kwargs = {
            "password": {"required": False, "allow_null": False},
            "email": {"required": False, "allow_null": False},
            "country_code": {"required": False, "allow_null": False},
            "login_count": {"required": False, "allow_null": False},
            "name": {"required": False, "allow_null": False},
            "username": {"required": False, "allow_null": False}
            }