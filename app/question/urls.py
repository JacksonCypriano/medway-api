from rest_framework.routers import DefaultRouter
from .viewsets import QuestionViewSet

router = DefaultRouter()
router.register(r"questions", QuestionViewSet, basename="questions")

urlpatterns = router.urls
