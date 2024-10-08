from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User  # or your custom user model
from .models import Profile  # Import your Profile model

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
