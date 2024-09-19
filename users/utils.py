# utils.py
from .models import Notification

def create_message_notification(sender, recipient):
    Notification.objects.create(
        user=recipient,
        message=f'{sender.username} sent you a message.'
    )

def create_follow_notification(follower, followed_user):
    Notification.objects.create(
        user=followed_user,
        message=f'{follower.username} started following you.'
    )
