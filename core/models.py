# core/models.py

from django.db import models
from django.conf import settings
import json

class Traveler(models.Model):
    # Link to User (OneToOne since one user can have one traveler profile)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="traveler_profile"
    )

    # Passport information
    passport_number = models.CharField(max_length=50, null=True, blank=True)
    passport_issuing_country = models.CharField(max_length=100, null=True, blank=True)
    passport_expiry_date = models.DateField(null=True, blank=True)

    # Risk-related info
    health_conditions = models.TextField(null=True, blank=True)
    frequent_traveler = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Traveler profile for {self.user.username if self.user else 'Unknown'}"


class Trip(models.Model):
    traveler = models.ForeignKey(
        Traveler,
        on_delete=models.CASCADE,
        related_name="trips"
    )

    destination_country = models.CharField(max_length=100)
    destination_city = models.CharField(max_length=100, null=True, blank=True)

    start_date = models.DateField()
    end_date = models.DateField()

    purpose = models.CharField(max_length=255)
    accommodation = models.CharField(max_length=255, null=True, blank=True)
    transport_mode = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.traveler} → {self.destination_country}"


class RiskAnalysisReport(models.Model):
    """
    Store risk analysis results from multi-agent system
    """
    RISK_LEVEL_CHOICES = [
        ("Low", "Low Risk"),
        ("Medium", "Medium Risk"),
        ("High", "High Risk"),
    ]
    
    trip = models.OneToOneField(
        Trip,
        on_delete=models.CASCADE,
        related_name="risk_analysis"
    )
    
    # Overall risk assessment
    overall_risk_score = models.IntegerField(default=0)  # 0-100
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES)
    
    # Individual agent scores
    weather_risk_score = models.IntegerField(default=0)
    disease_risk_score = models.IntegerField(default=0)
    
    # Full report as JSON
    full_report = models.JSONField(default=dict)
    
    # Summary data (extracted from full report)
    top_risks = models.JSONField(default=list)  # List of top risks
    recommendations = models.JSONField(default=list)  # List of recommendations
    executive_summary = models.TextField(blank=True)
    
    # Agent reports
    weather_report = models.JSONField(default=dict)
    disease_report = models.JSONField(default=dict)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Risk Analysis for {self.trip} - {self.risk_level}"
    
    def save(self, *args, **kwargs):
        """Ensure risk_level is set based on overall_risk_score"""
        if self.overall_risk_score < 30:
            self.risk_level = "Low"
        elif self.overall_risk_score < 60:
            self.risk_level = "Medium"
        else:
            self.risk_level = "High"
        super().save(*args, **kwargs)
