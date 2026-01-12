from rest_framework.routers import DefaultRouter
from .viewsets import StudentViewSet

router = DefaultRouter()
router.register(r"students", StudentViewSet, basename="students")

urlpatterns = router.urls
