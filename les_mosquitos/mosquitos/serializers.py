from rest_framework import serializers
from django.contrib.auth.models import User

from .models import (
    Parcours,
    Label,
    Point,
    ParcoursPoint,
    Intervention,
    PointPhoto,
    MissionTrack,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ["id", "name", "color"]


class PointPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointPhoto
        fields = ["id", "point", "image", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]


class MultiPointPhotoUploadSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.ImageField(), allow_empty=False)


class PointSerializer(serializers.ModelSerializer):
    label = LabelSerializer(read_only=True)

    label_id = serializers.PrimaryKeyRelatedField(
        queryset=Label.objects.all(), source="label", write_only=True
    )

    photos = PointPhotoSerializer(many=True, read_only=True)

    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Point
        fields = [
            "id",
            "name",
            "description",
            "latitude",
            "longitude",
            "comment",
            "label",
            "label_id",
            "label__is_treatable",
            "photos",
            "is_treated",
            "last_treatment_date",
            "created_by",
            "created_at",
            "updated_at",
        ]


class ParcoursPointSerializer(serializers.ModelSerializer):
    point = PointSerializer(read_only=True)

    point_id = serializers.PrimaryKeyRelatedField(
        queryset=Point.objects.all(), source="point", write_only=True
    )

    class Meta:
        model = ParcoursPoint
        fields = [
            "id",
            "point",
            "point_id",
            "visit_order",
            "is_completed_in_mission",
            "completed_at",
        ]


class ParcoursSerializer(serializers.ModelSerializer):
    parcours_points = ParcoursPointSerializer(many=True, read_only=True)

    class Meta:
        model = Parcours
        fields = [
            "id",
            "name",
            "description",
            "distance_km",
            "duration_min",
            "planned_path",
            "created_at",
            "started_at",
            "finished_at",
            "parcours_points",
        ]


class InterventionSerializer(serializers.ModelSerializer):
    point = PointSerializer(read_only=True)

    point_id = serializers.PrimaryKeyRelatedField(
        queryset=Point.objects.all(), source="point", write_only=True
    )

    performed_by = UserSerializer(read_only=True)

    class Meta:
        model = Intervention
        fields = [
            "id",
            "point",
            "point_id",
            "intervention_type",
            "comment",
            "performed_by",
            "performed_at",
        ]


class MissionTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionTrack
        fields = [
            "id",
            "parcours",
            "latitude",
            "longitude",
            "recorded_at",
        ]
