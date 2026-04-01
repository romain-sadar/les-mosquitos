import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Label(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name


class Point(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    latitude = models.FloatField()
    longitude = models.FloatField()

    label = models.ForeignKey(Label, on_delete=models.SET_NULL, null=True)

    comment = models.TextField(blank=True)

    is_treated = models.BooleanField(default=False)

    last_treatment_date = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def check_treatment_status(self):
        if self.is_treated and self.last_treatment_date:
            if timezone.now() - self.last_treatment_date > timedelta(weeks=6):
                self.is_treated = False
                self.save()

    def __str__(self):
        return self.name


class PointPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    point = models.ForeignKey(Point, related_name="photos", on_delete=models.CASCADE)

    image = models.ImageField(upload_to="points/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Parcours(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    distance_km = models.FloatField(default=0)
    duration_min = models.IntegerField(default=0)

    planned_path = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    started_at = models.DateTimeField(null=True, blank=True)

    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class ParcoursPoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    parcours = models.ForeignKey(
        Parcours, related_name="parcours_points", on_delete=models.CASCADE
    )

    point = models.ForeignKey(Point, on_delete=models.CASCADE)

    visit_order = models.IntegerField()

    is_completed_in_mission = models.BooleanField(default=False)

    completed_at = models.DateTimeField(null=True, blank=True)


class Intervention(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    point = models.ForeignKey(
        Point, related_name="interventions", on_delete=models.CASCADE
    )

    comment = models.TextField(blank=True)

    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    performed_at = models.DateTimeField(auto_now_add=True)


class MissionTrack(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    parcours = models.ForeignKey(
        Parcours, related_name="gps_tracks", on_delete=models.CASCADE
    )

    latitude = models.FloatField()
    longitude = models.FloatField()

    recorded_at = models.DateTimeField(auto_now_add=True)


class UserActivity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ACTION_CHOICES = [
        ("create_point", "Create Point"),
        ("treat_point", "Treat Point"),
        ("create_parcours", "Create Parcours"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)

    point = models.ForeignKey(Point, null=True, blank=True, on_delete=models.CASCADE)

    parcours = models.ForeignKey(
        Parcours, null=True, blank=True, on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)
