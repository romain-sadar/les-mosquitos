from django.db import models
from django.contrib.auth.models import User

import uuid


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Parcours(UUIDModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    distance_km = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    duration_min = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def total_points(self):
        return self.mission_points.count()

    @property
    def treated_points(self):
        return self.mission_points.filter(is_completed_in_mission=True).count()


class Label(UUIDModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Point(UUIDModel):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    photo = models.ImageField(upload_to="points/", blank=True, null=True)
    comment = models.TextField(blank=True)

    label = models.ForeignKey(Label, on_delete=models.CASCADE, related_name="points")

    is_treated = models.BooleanField(default=False)
    last_treatment_date = models.DateField(blank=True, null=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_points",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class ParcoursPoint(UUIDModel):
    """
    Association mission <-> points avec ordre de visite.
    C'est ici que l'algo écrit son résultat.
    """

    parcours = models.ForeignKey(
        Parcours, on_delete=models.CASCADE, related_name="parcours_points"
    )
    point = models.ForeignKey(
        Point, on_delete=models.CASCADE, related_name="parcours_points"
    )

    visit_order = models.PositiveIntegerField()
    is_completed_in_mission = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["visit_order"]
        unique_together = ("parcours", "point")

    def __str__(self):
        return f"{self.parcours.name} - {self.point.name} ({self.visit_order})"


class UserActivity(UUIDModel):
    """
    Pour l'écran Profil / Historique utilisateur.
    """

    ACTION_TYPES = [
        ("point_added", "Ajout d’un point"),
        ("point_treated", "Traitement d’un point"),
        ("mission_created", "Création d’une cartographie"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")

    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)

    point = models.ForeignKey(
        Point,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )

    parcours = models.ForeignKey(
        Parcours,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.action_type}"


class Intervention(UUIDModel):
    """
    Historique visible dans l'écran "Historique".
    On garde un snapshot du label pour figer l'affichage historique.
    """

    INTERVENTION_TYPES = [
        ("added", "Ajout"),
        ("treated", "Traité"),
        ("updated", "Mis à jour"),
        ("checked", "Vérifié"),
    ]

    point = models.ForeignKey(
        Point, on_delete=models.CASCADE, related_name="interventions"
    )

    intervention_type = models.CharField(max_length=20, choices=INTERVENTION_TYPES)

    comment = models.TextField(blank=True)

    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interventions_done",
    )

    performed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-performed_at"]

    def __str__(self):
        return f"{self.get_intervention_type_display()} - {self.point.name}"
