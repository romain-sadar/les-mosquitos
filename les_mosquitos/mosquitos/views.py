from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated

from collections import defaultdict

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
import requests
import os


from .models import (
    Parcours,
    Point,
    Label,
    Intervention,
    ParcoursPoint,
    MissionTrack,
    PointPhoto,
)

from .serializers import (
    ParcoursSerializer,
    PointSerializer,
    LabelSerializer,
    InterventionSerializer,
    ParcoursPointSerializer,
    MissionTrackSerializer,
    PointPhotoSerializer,
)


from rest_framework.authtoken.models import Token


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                },
            }
        )


class RegisterView(APIView):
    permission_classes = [AllowAny]

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
                {"error": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(username=username, password=password)
        token = Token.objects.create(user=user)

        return Response(
            {
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LabelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Label.objects.all()
    serializer_class = LabelSerializer


class PointViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Point.objects.select_related("label", "created_by").prefetch_related(
        "photos"
    )
    serializer_class = PointSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        for point in queryset:
            point.check_treatment_status()
        return queryset

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        point = serializer.save(created_by=user)

        Intervention.objects.create(
            point=point,
            intervention_type="added",
            performed_by=user,
        )

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        point = self.get_object()
        interventions = point.interventions.select_related("performed_by")
        serializer = InterventionSerializer(interventions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def mark_treated(self, request, pk=None):
        point = self.get_object()

        if not point.label or not point.label.is_treatable:
            return Response({"error": "Point is not treatable"}, status=400)

        if not point.is_treated:
            point.is_treated = True
            point.last_treatment_date = timezone.now()
            point.save()

            Intervention.objects.create(
                point=point,
                intervention_type="treated",
                performed_by=request.user,
            )

        return Response({"status": "treated"})


class PointPhotoViewSet(ModelViewSet):
    serializer_class = PointPhotoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PointPhoto.objects.filter(point_id=self.kwargs["point_pk"])

    def create(self, request, *args, **kwargs):
        point_id = self.kwargs["point_pk"]

        point = Point.objects.get(id=point_id)
        if point.created_by != request.user:
            return Response({"error": "Forbidden"}, status=403)

        images = request.FILES.getlist("images")

        if not images:
            return Response({"error": "No images provided"}, status=400)

        photos = [PointPhoto(point_id=point_id, image=image) for image in images]

        created_photos = PointPhoto.objects.bulk_create(photos)

        return Response(
            PointPhotoSerializer(created_photos, many=True).data,
            status=201,
        )


class ParcoursViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Parcours.objects.prefetch_related("parcours_points__point")
    serializer_class = ParcoursSerializer

    def perform_destroy(self, instance):
        point_ids = list(
            instance.parcours_points.values_list("point_id", flat=True).distinct()
        )
        with transaction.atomic():
            instance.delete()
            for pid in point_ids:
                if not ParcoursPoint.objects.filter(point_id=pid).exists():
                    Point.objects.filter(pk=pid).delete()

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        parcours = self.get_object()
        point_ids = parcours.parcours_points.values_list("point_id", flat=True)
        interventions = (
            Intervention.objects.filter(point_id__in=point_ids)
            .select_related("point", "performed_by")
            .order_by("performed_at")
        )

        grouped = defaultdict(list)
        for intervention in interventions:
            grouped[intervention.point.id].append(
                InterventionSerializer(intervention).data
            )

        return Response(grouped)

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

    @action(detail=True, methods=["get"])
    def optimize(self, request, pk=None):
        start_lat = request.query_params.get("start_lat")
        start_lng = request.query_params.get("start_lng")
        parcours = self.get_object()

        parcours_points = (
            parcours.parcours_points.select_related("point")
            .filter(point__is_treated=False)
            .order_by("visit_order")
        )

        if parcours_points.count() < 2:
            return Response(
                {"error": "Minimum 2 points required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        coordinates_list = []

        if start_lat and start_lng:
            coordinates_list.append(f"{start_lng},{start_lat}")

        coordinates_list.extend([
            f"{pp.point.longitude},{pp.point.latitude}"
            for pp in parcours_points
        ])

        coordinates = ";".join(coordinates_list)

        token = os.getenv("MAPBOX_TOKEN")

        url = (
            f"https://api.mapbox.com/optimized-trips/v1/mapbox/walking/{coordinates}"
            f"?geometries=geojson"
            f"&source=first"
            f"&destination=any"
            f"&roundtrip=false"
            f"&access_token={token}"
        )

        response = requests.get(url, timeout=10)
        data = response.json()

        if "trips" not in data:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        trip = data["trips"][0]

        ordered_waypoints = sorted(data["waypoints"], key=lambda x: x["waypoint_index"])

        original_points = list(parcours_points)

        optimized_points = []

        for wp in ordered_waypoints:
            original_idx = wp["waypoint_index"]
            pp = original_points[original_idx]

            optimized_points.append({
                "point_id": str(pp.point.id),
                "name": pp.point.name,
                "latitude": pp.point.latitude,
                "longitude": pp.point.longitude,
                "optimized_order": original_idx
            })

        distance_km = round(trip["distance"] / 1000, 2)
        duration_min = round(trip["duration"] / 60)

        return Response(
            {
                "distance_km": distance_km,
                "duration_min": duration_min,
                "geometry": trip["geometry"],
                "optimized_points": optimized_points,
            }
        )


class ParcoursPointViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ParcoursPoint.objects.select_related("parcours", "point")
    serializer_class = ParcoursPointSerializer


class InterventionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Intervention.objects.select_related("point", "performed_by")
    serializer_class = InterventionSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(performed_by=user)


class MissionTrackViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = MissionTrack.objects.select_related("parcours")
    serializer_class = MissionTrackSerializer
