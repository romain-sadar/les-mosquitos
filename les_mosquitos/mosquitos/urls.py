from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LoginView,
    RegisterView,
    LabelViewSet,
    PointViewSet,
    ParcoursViewSet,
    ParcoursPointViewSet,
    InterventionViewSet,
    MissionTrackViewSet,
)

router = DefaultRouter()

router.register(r"labels", LabelViewSet)
router.register(r"points", PointViewSet)
router.register(r"parcours", ParcoursViewSet)
router.register(r"parcours-points", ParcoursPointViewSet)
router.register(r"interventions", InterventionViewSet)
router.register(r"mission-tracks", MissionTrackViewSet)

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("register/", RegisterView.as_view()),
    path("", include(router.urls)),
]
