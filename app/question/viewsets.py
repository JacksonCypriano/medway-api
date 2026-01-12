from rest_framework import viewsets
from question.models import Question
from question.serializers import QuestionSerializer


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.all().prefetch_related("alternatives")
    serializer_class = QuestionSerializer
