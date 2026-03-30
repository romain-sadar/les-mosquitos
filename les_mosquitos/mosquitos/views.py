from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Parcours, Point, Label, Intervention, ParcoursPoint
from .serializers import (
    ParcoursSerializer,
    PointSerializer,
    LabelSerializer,
    InterventionSerializer,
    ParcoursPointSerializer,
)
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


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


class ParcoursViewSet(ModelViewSet):
    queryset = Parcours.objects.all().prefetch_related("parcours_points__point")
    serializer_class = ParcoursSerializer


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


class LabelViewSet(ReadOnlyModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer


class InterventionViewSet(ModelViewSet):
    queryset = Intervention.objects.select_related("point", "performed_by")
    serializer_class = InterventionSerializer


class ParcoursPointViewSet(ModelViewSet):
    queryset = ParcoursPoint.objects.select_related("parcours", "point")
    serializer_class = ParcoursPointSerializer
