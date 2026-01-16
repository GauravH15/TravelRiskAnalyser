from rest_framework import serializers
from .models import Traveler, Trip, RiskAnalysisReport


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


class RiskAnalysisReportSerializer(serializers.ModelSerializer):
    """
    Serializer for risk analysis reports from multi-agent system
    """
    class Meta:
        model = RiskAnalysisReport
        fields = [
            "id",
            "trip",
            "overall_risk_score",
            "risk_level",
            "weather_risk_score",
            "disease_risk_score",
            "top_risks",
            "recommendations",
            "executive_summary",
            "weather_report",
            "disease_report",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "overall_risk_score",
            "risk_level",
            "weather_risk_score",
            "disease_risk_score",
            "top_risks",
            "recommendations",
            "executive_summary",
            "weather_report",
            "disease_report",
            "created_at",
            "updated_at",
        )