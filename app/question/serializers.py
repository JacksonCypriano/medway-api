from rest_framework import serializers
from .models import Question, Alternative


class AlternativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternative
        fields = ["id", "content", "option", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    alternatives = AlternativeSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "content", "alternatives"]
