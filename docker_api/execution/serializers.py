from rest_framework import serializers
from .models import CodeExecution
from django.contrib.auth.models import User

class CodeExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeExecution
        fields = ['id', 'language_version', 'code', 'output', 'status', 'execution_time', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user  # Добавляем `user` автоматически
        return super().create(validated_data)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user