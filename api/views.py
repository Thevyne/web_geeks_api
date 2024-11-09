from django.contrib.auth.models import User
from rest_framework import views, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from api.serializers import AiResponseSerializer, UserSerializer, TokenSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from api.models import AiDoctor 

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
import requests

from rest_framework.permissions import IsAuthenticated
from django.conf import settings


from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated  # Optional, use if needed
from groq import Groq
import os
from .utils import send_code_to_groq
from django.contrib.auth.forms import SetPasswordForm

class AiResponseView(views.APIView):
    serializer_class = AiResponseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Return all stored AI responses
        qs = AiDoctor.objects.all()
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        # Validate input data
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Prepare the prompt
            _input = serializer.validated_data["_input"]

            # Call the Groq API to generate response
            groq_response = send_code_to_groq(_input)
            if "error" in groq_response:
                return Response({"error": groq_response["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Save the response
            serializer.save(_output=groq_response["output"])
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserView(views.APIView):
    serializer_class = UserSerializer
    def get(self, request, format=None):
        qs = User.objects.all()
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TokenView(ObtainAuthToken):
    serializer_class = TokenSerializer


class PasswordResetRequestAPI(views.APIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(user.pk.encode())
                reset_url = f"{settings.FRONTEND_URL}/reset-password/{uidb64}/{token}/"  # Adjust frontend URL as needed
                
                # Send email
                subject = "Password Reset Request"
                message = render_to_string('password_reset_email.html', {
                    'reset_url': reset_url,
                    'user': user
                })
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

                return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "Email not found."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Password reset confirm: user enters new password after clicking reset link
class PasswordResetConfirmAPI(views.APIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError):
            return Response({"error": "Invalid user or token."}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                new_password = serializer.validated_data['new_password']
                user.set_password(new_password)
                user.save()

                return Response({"message": "Password successfully reset."}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
    