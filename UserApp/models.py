# user/models.py

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
import uuid

class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        HR_MANAGER = "hr_manager", "HR Manager"
        TRAVELER = "traveler", "Traveler"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TRAVELER
    )

    # Basic personal info
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    nationality = models.CharField(max_length=120, null=True, blank=True)

    # Optional organization fields
    department = models.CharField(max_length=120, blank=True, null=True)
    job_title = models.CharField(max_length=120, blank=True, null=True)
    employee_id = models.CharField(max_length=50, blank=True, null=True, unique=True)

    # User preferences
    timezone = models.CharField(max_length=50, default="UTC")

    # Important: override groups and permissions to avoid reverse accessor clashes
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups"
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
