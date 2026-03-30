from django.contrib import admin
from .models import Parcours, Label, Point


@admin.register(Parcours)
class ParcoursAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "distance_km", "duration_min", "created_at")
    search_fields = ("name", "description")
    list_filter = ("created_at",)


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude")
    search_fields = ("name",)
