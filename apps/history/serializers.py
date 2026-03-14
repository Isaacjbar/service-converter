from rest_framework import serializers
from .models import DiagramHistory


class DiagramHistoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagramHistory
        fields = ['id', 'filename', 'version', 'created_at']


class DiagramHistoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagramHistory
        fields = [
            'id', 'filename', 'source_code',
            'class_diagram', 'usecase_diagram', 'flow_diagram',
            'version', 'created_at',
        ]
