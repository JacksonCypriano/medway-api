from rest_framework.routers import DefaultRouter
from .viewsets import ExamViewSet, ExamSubmissionViewSet

router = DefaultRouter()
router.register(r"exams", ExamViewSet, basename="exams")
router.register(r"submissions", ExamSubmissionViewSet, basename="submissions")

urlpatterns = router.urls
