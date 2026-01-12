from rest_framework import serializers
from .models import Exam, ExamQuestion, ExamSubmission, ExamSubmissionAnswer
from question.models import Question
from question.serializers import QuestionSerializer


class ExamSubmissionAnswerSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    selected_option = serializers.IntegerField()

    class Meta:
        model = ExamSubmissionAnswer
        fields = ["question", "selected_option"]

    def validate(self, data):
        question = data["question"]
        selected_option = data["selected_option"]

        if not question.alternatives.filter(option=selected_option).exists():
            raise serializers.ValidationError(
                f"A opção {selected_option} não pertence a essa questão."
            )
        return data


class ExamSubmissionSerializer(serializers.ModelSerializer):
    answers = ExamSubmissionAnswerSerializer(many=True)


    class Meta:
        model = ExamSubmission
        fields = ["id", "student", "exam", "created_at", "answers"]
        read_only_fields = ["id", "created_at"]

    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError(
                "É necessário enviar pelo menos uma resposta."
            )
        return value

    def validate(self, data):
        submission = self.context.get("submission")
        student = data["student"]
        answers = data["answers"]
        for answer in answers:
            question = answer["question"]

            if submission.answers.filter(submission__student=student, question=question).exists():
                raise serializers.ValidationError(
                    f"A pergunta {question.id} já foi respondida nesta submissão."
                )

            if not question.alternatives.filter(option=answer["selected_option"]).exists():
                raise serializers.ValidationError(
                    f"A opção {answer['selected_option']} não pertence a pergunta {question.id}."
                )

        return data

    def create(self, validated_data):
        answers_data = validated_data.pop("answers")
        submission = ExamSubmission.objects.create(**validated_data)

        for answer in answers_data:
            ExamSubmissionAnswer.objects.create(
                submission=submission,
                question=answer["question"],
                selected_option=answer["selected_option"]
            )

        return submission
    
    def update(self, instance, validated_data):
        answers_data = validated_data.pop("answers", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if answers_data:
            for answer in answers_data:
                q = answer["question"]
                selected_option = answer["selected_option"]
                obj, created = ExamSubmissionAnswer.objects.update_or_create(
                    submission=instance,
                    question=q,
                    defaults={"selected_option": selected_option},
                )
        return instance


class ExamSubmissionResultSerializer(serializers.ModelSerializer):
    results = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = ExamSubmission
        fields = ["student", "exam", "results", "score", "percentage"]

    def get_results(self, obj):
        results = []
        for answer in obj.answers.all():
            correct_alt = answer.question.alternatives.filter(is_correct=True).first()
            correct_option = correct_alt.option if correct_alt else None
            results.append({
                "question": answer.question.id,
                "selected_option": answer.selected_option,
                "correct_option": correct_option,
                "is_correct": answer.selected_option == correct_option if correct_option is not None else False,
            })
        return results

    def get_score(self, obj):
        answers = obj.answers.all()
        correct = 0
        for a in answers:
            correct_alt = a.question.alternatives.filter(is_correct=True).first()
            correct_option = correct_alt.option if correct_alt else None
            if a.selected_option == correct_option:
                correct += 1
        return {"correct": correct, "total": answers.count()}

    def get_percentage(self, obj):
        score = self.get_score(obj)
        return round(score["correct"] / score["total"] * 100, 2) if score["total"] else 0

class ExamQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = ExamQuestion
        fields = ["number", "question"]


class ExamSerializer(serializers.ModelSerializer):
    questions = ExamQuestionSerializer(
        source="examquestion_set",
        many=True,
        read_only=True
    )

    class Meta:
        model = Exam
        fields = ["id", "name", "questions"]
