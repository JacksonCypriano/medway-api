from django.db import models

from question.models import Question
from student.models import Student

class Exam(models.Model):
    name = models.CharField(max_length=100)
    questions = models.ManyToManyField(Question, through='ExamQuestion', related_name='questions')

    def __str__(self) -> str:
        return self.name


class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()

    class Meta:
        unique_together = ('exam', 'number')
        ordering = ['number']

    def __str__(self) -> str:
        return f"{self.exam.name} - {self.number}"


class ExamSubmission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.student} - {self.exam.name}"


class ExamSubmissionAnswer(models.Model):
    submission = models.ForeignKey(
        ExamSubmission,
        related_name="answers",
        on_delete=models.CASCADE
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.submission.student} - {self.question.id}"
