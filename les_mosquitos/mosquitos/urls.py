from django.urls import path, include
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter


from .views import (
    LoginView,
    RegisterView,
    LabelViewSet,
    PointViewSet,
    ParcoursViewSet,
    ParcoursPointViewSet,
    InterventionViewSet,
    MissionTrackViewSet,
    PointPhotoViewSet,
)

router = DefaultRouter()
router.register(r"points", PointViewSet)
router.register(r"labels", LabelViewSet)
router.register(r"parcours", ParcoursViewSet)
router.register(r"parcours-points", ParcoursPointViewSet)
router.register(r"interventions", InterventionViewSet)
router.register(r"mission-tracks", MissionTrackViewSet)

# 👇 nested router
points_router = NestedDefaultRouter(router, r"points", lookup="point")
points_router.register(r"photos", PointPhotoViewSet, basename="point-photos")

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("register/", RegisterView.as_view()),
    path("", include(router.urls)),
    path("", include(points_router.urls)),
]