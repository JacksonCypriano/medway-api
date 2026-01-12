from django.db import models

from question.utils import AlternativesChoices


class Question(models.Model):
    content = models.TextField()

    def __str__(self) -> str:
        return self.content

    @property
    def correct_option(self) -> int | None:
        correct = Alternative.objects.filter(question=self, is_correct=True).first()
        return correct.option if correct else None


class Alternative(models.Model):
    question = models.ForeignKey(Question, related_name='alternatives', on_delete=models.CASCADE)
    content = models.TextField()
    option = models.IntegerField(choices=AlternativesChoices)
    is_correct = models.BooleanField(null=True)

    def __str__(self) -> str:
        return f"{self.question.id} - {self.content}"
