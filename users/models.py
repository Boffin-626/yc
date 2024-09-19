from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_delete
from inaEthe.models import Category, Content
from django.urls import reverse

class CustomUser(AbstractUser):
    bio = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    email_verified = models.BooleanField(default=False)  # Email verification
    two_factor_auth = models.BooleanField(default=False)  # Two-factor authentication
    preferred_categories = models.ManyToManyField(Category, blank=True, related_name="preferred_by_users")
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    likes = models.ManyToManyField(Content, related_name='liked_by')

    def follow(self, user):
        """Adds a user to the following list."""
        self.following.add(user)

    def unfollow(self, user):
        """Removes a user from the following list."""
        self.following.remove(user)

    def is_following(self, user):
        """Check if the user is following another user."""
        return self.following.filter(id=user.id).exists()
    
class Profile(models.Model):
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('friends', 'Friends Only'),
        ('private', 'Private'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    privacy_level = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public')
    notification_emails = models.BooleanField(default=True)  # Control email alerts

    def delete_profile(self):
        """Deletes the user and profile associated with it."""
        self.user.delete()

# Automatically delete profile picture file when Profile is deleted
@receiver(post_delete, sender=Profile)
def delete_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture:
        instance.profile_picture.delete(False)

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Message from {self.sender} to {self.recipient}'

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        # This returns the URL to which the notification links
        return reverse('notification_detail', args=[str(self.id)])

    def __str__(self):
        return f'Notification for {self.user.username}: {self.message}'
    
# Payment Method Model
class PaymentMethod(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    expiry_date = models.CharField(max_length=5)
    card_holder_name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.card_holder_name} - {self.card_number[-4:]}'
