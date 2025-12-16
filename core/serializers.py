from rest_framework import serializers
from .models import Traveler, Trip


class TravelerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traveler
        fields = "__all__"
        read_only_fields = ("created_at", "user")


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = "__all__"
        read_only_fields = ("created_at",)