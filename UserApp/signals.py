from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from core.models import Traveler


@receiver(post_save, sender=User)
def create_traveler_profile(sender, instance, created, **kwargs):
    if created and instance.role == User.Role.TRAVELER:
        Traveler.objects.create(user=instance)
