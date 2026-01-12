from django.core.exceptions import ValidationError
from django.http import Http404

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError as DRFValidationError
from rest_framework.pagination import PageNumberPagination

from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

import logging
import traceback

from exam.models import Exam, ExamQuestion, ExamSubmission
from exam.serializers import ExamSerializer, ExamSubmissionSerializer, ExamSubmissionResultSerializer
from student.models import Student

logger = logging.getLogger(__name__)


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)

        except Http404:
            logger.warning(f"Tentativa de acessar exame inexistente: ID={kwargs.get('pk')}")
            raise NotFound("Exame não encontrado.")

        except Exception as e:
            logger.error(f"Erro inesperado ao buscar exame {kwargs.get('pk')}: {e}")
            logger.error(traceback.format_exc())
            return Response(
                {"detail": "Erro interno ao buscar exame."},
                status=500
            )

    @extend_schema(
        summary="Listar questões de um exame",
        description="Retorna todas as questões atribuídas ao exame, na ordem correta."
    )
    @action(detail=True, methods=["get"])
    def questions(self, request, pk=None):
        try:
            try:
                exam = self.get_object()
            except Http404:
                logger.warning(f"Tentativa de acessar exame inexistente: ID={pk}")
                raise NotFound("Exame não encontrado.")

            exam_questions = (
                ExamQuestion.objects.filter(exam=exam)
                .select_related("question")
                .prefetch_related("question__alternatives")
            )

            paginator = PageNumberPagination()
            paginator.page_size = 10
            result_page = paginator.paginate_queryset(exam_questions, request)

            data = [
                {
                    "id": eq.question.id,
                    "content": eq.question.content,
                    "order": eq.number,
                    "alternatives": [
                        {
                            "option": alt.option,
                            "content": alt.content,
                            "is_correct": alt.is_correct,
                        }
                        for alt in eq.question.alternatives.all()
                    ],
                }
                for eq in result_page
            ]

            logger.info(f"Exam {pk} listado com {len(data)} questões.")
            return paginator.get_paginated_response(data)

        except NotFound:
            raise

        except Exception as e:
            logger.error(
                f"Erro inesperado ao listar questões do exame {pk}: {e}\n{traceback.format_exc()}"
            )
            return Response(
                {"detail": "Erro interno ao buscar questões do exame."},
                status=500,
            )

class ExamSubmissionViewSet(viewsets.ModelViewSet):
    queryset = ExamSubmission.objects.all()
    serializer_class = ExamSubmissionSerializer

    def get_serializer_class(self):
        if self.action == "result":
            return ExamSubmissionResultSerializer
        return ExamSubmissionSerializer

    @extend_schema(
        summary="Enviar respostas de um exame",
        description="Recebe todas as respostas do aluno e cria uma submissão."
    )
    def create(self, request, *args, **kwargs):
        logger.info("Recebendo nova submissão de prova...")
        logger.debug(f"Payload recebido: {request.data}")

        try:
            student_id = request.data.get("student")
            exam_id = request.data.get("exam")

            submission, created = ExamSubmission.objects.get_or_create(
                student_id=student_id,
                exam_id=exam_id,
                defaults={"student_id": student_id, "exam_id": exam_id}
            )

            serializer = self.get_serializer(
                submission,
                data=request.data,
                context={"submission": submission}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            logger.info("Submissão criada/atualizada com sucesso!")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except DRFValidationError as ve:
            logger.warning("Erro de validação ao criar submissão.")
            logger.warning(str(ve))
            return Response(
                {"detail": "Erro de validação", "errors": ve.detail},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error("Erro inesperado ao criar submissão de prova.")
            logger.error(str(e))
            logger.debug(traceback.format_exc())
            return Response({"detail": "Erro interno."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Resultado da prova",
        description="Retorna questões corretas, erradas, score e porcentagem.",
        responses=ExamSubmissionResultSerializer
    )
    @action(detail=True, methods=["get"])
    def result(self, request, pk=None):
        logger.info(f"Consultando resultado da submissão ID={pk}")

        try:
            submission = ExamSubmission.objects.get(pk=pk)
            serializer = ExamSubmissionResultSerializer(submission)
            logger.info("Resultado retornado com sucesso.")

            return Response(serializer.data)

        except ExamSubmission.DoesNotExist:
            logger.warning(f"Tentativa de acesso a submissão inexistente ID={pk}")
            return Response({"detail": "Resposta do aluno não encontrada."}, status=404)

        except Exception as e:
            logger.error("Erro inesperado ao obter resultado.")
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return Response({"detail": "Erro interno."}, status=500)
