from rest_framework import serializers
from .models import CodeExecution

class CodeExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeExecution
        fields = ['id', 'language', 'code', 'output', 'status', 'execution_time', 'created_at']  # Убираем `user`

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user  # Добавляем `user` автоматически
        return super().create(validated_data)