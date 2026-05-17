from rest_framework import serializers
from .models import Run, User


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name']
