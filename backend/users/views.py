# users/views.py
from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserSerializer
from .models import User

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]   # Anyone can register (you can restrict later)
    queryset = User.objects.all()
    serializer_class = RegisterSerializer