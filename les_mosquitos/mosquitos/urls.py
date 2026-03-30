from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    LoginView,
    ParcoursViewSet,
    PointViewSet,
    LabelViewSet,
    InterventionViewSet,
    ParcoursPointViewSet,
)

router = DefaultRouter()
router.register("parcours", ParcoursViewSet)
router.register("points", PointViewSet)
router.register("labels", LabelViewSet)
router.register("interventions", InterventionViewSet)
router.register("parcours-points", ParcoursPointViewSet)

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("", include(router.urls)),
]
