# core/models.py

from django.db import models
from django.conf import settings

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
