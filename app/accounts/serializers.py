from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from .utils import Util


class UserSerializer(serializers.ModelSerializer):
    """Serializers for the user object"""
    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'name',
            'email',
            'password',
            'cpf',
            'phone',
            'street',
            'state',
            'city',
            'zip_code',
            'complement'
        )
        extra_kwargs = {'password': {'write_only': True, 'min_length': 7},
                        'id': {'read_only': True}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

    def validate_cpf(self, cpf):
        if not Util.validate_cpf(cpf):
            raise serializers.ValidationError('Type a valid CPF')
        return cpf

    def validate_phone(self, phone):
        if not Util.validate_phone(phone):
            raise serializers.ValidationError('Type a valid Phone Number')
        return phone


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password',
                                            'trim_whitespace': False})

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
