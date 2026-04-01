from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from .models import (
    Parcours,
    Point,
    Label,
    Intervention,
    ParcoursPoint,
    MissionTrack,
)

from .serializers import (
    ParcoursSerializer,
    PointSerializer,
    LabelSerializer,
    InterventionSerializer,
    ParcoursPointSerializer,
    MissionTrackSerializer,
)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(
            {
                "id": user.id,
                "username": user.username,
            }
        )


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(username=username, password=password)

        return Response(
            {
                "id": user.id,
                "username": user.username,
            },
            status=status.HTTP_201_CREATED,
        )


class LabelViewSet(ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer


class PointViewSet(ModelViewSet):
    queryset = Point.objects.select_related("label", "created_by")
    serializer_class = PointSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        point = self.get_object()
        interventions = point.interventions.select_related("performed_by")
        serializer = InterventionSerializer(interventions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def mark_treated(self, request, pk=None):
        point = self.get_object()

        point.is_treated = True
        point.last_treatment_date = timezone.now()
        point.save()

        return Response({"status": "treated"})


class ParcoursViewSet(ModelViewSet):
    queryset = Parcours.objects.prefetch_related("parcours_points__point")
    serializer_class = ParcoursSerializer

    @action(detail=True, methods=["post"])
    def add_point(self, request, pk=None):
        parcours = self.get_object()
        point_id = request.data.get("point_id")

        try:
            point = Point.objects.get(id=point_id)
        except Point.DoesNotExist:
            return Response(
                {"error": "Point not found"}, status=status.HTTP_404_NOT_FOUND
            )

        order = parcours.parcours_points.count() + 1

        ParcoursPoint.objects.create(parcours=parcours, point=point, visit_order=order)

        return Response({"status": "point ajouté"})


class ParcoursPointViewSet(ModelViewSet):
    queryset = ParcoursPoint.objects.select_related("parcours", "point")
    serializer_class = ParcoursPointSerializer


class InterventionViewSet(ModelViewSet):
    queryset = Intervention.objects.select_related("point", "performed_by")
    serializer_class = InterventionSerializer

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)


class MissionTrackViewSet(ModelViewSet):
    queryset = MissionTrack.objects.select_related("parcours")
    serializer_class = MissionTrackSerializer
