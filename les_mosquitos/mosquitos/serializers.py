from rest_framework import serializers
from django.contrib.auth.models import User

from .models import (
    Parcours,
    Label,
    Point,
    ParcoursPoint,
    UserActivity,
    Intervention,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ["id", "name"]


class PointSerializer(serializers.ModelSerializer):
    label = LabelSerializer(read_only=True)
    label_id = serializers.PrimaryKeyRelatedField(
        queryset=Label.objects.all(), source="label", write_only=True
    )

    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Point
        fields = [
            "id",
            "name",
            "latitude",
            "longitude",
            "photo",
            "comment",
            "label",
            "label_id",
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

    total_points = serializers.IntegerField(read_only=True)
    treated_points = serializers.IntegerField(read_only=True)

    class Meta:
        model = Parcours
        fields = [
            "id",
            "name",
            "description",
            "distance_km",
            "duration_min",
            "created_at",
            "started_at",
            "finished_at",
            "parcours_points",
            "total_points",
            "treated_points",
        ]


class UserActivitySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    point = PointSerializer(read_only=True)
    parcours = ParcoursSerializer(read_only=True)

    class Meta:
        model = UserActivity
        fields = [
            "id",
            "user",
            "action_type",
            "point",
            "parcours",
            "created_at",
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
