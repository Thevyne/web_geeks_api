from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from api.models import AiDoctor
from api.utils import send_code_to_api

class AiResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiDoctor
        fields = ("id","_input","_output")
        extra_kwargs = {
            "_output":{"read_only":True}
        }

    def create(self, validated_data):
        ad = AiDoctor(**validated_data)
        _output = send_code_to_api(validated_data["_input"])
        ad._output = _output
        ad.save()
        return ad 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        extra_kwargs = {
            "password":{"write_only":True}
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        # to save the password as hashed and crypted
        user.set_password(password)
        user.save()

        Token.objects.create(user=user)
        return user

class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={"input_type":"password"}, trim_whitespace=False)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        user = authenticate(request=self.context.get("request"), username=username, password=password)
        if not user:
            msg = "Credentials are not provided corectly..."
            raise serializers.ValidationError(msg, code="authentication")

        attrs["user"] = user
        return attrs