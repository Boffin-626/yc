from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import *
from .models import *

from inaEthe.models import Book, Purchase  # Import Book model from its app
from .utils import create_message_notification, create_follow_notification  # Import the utility functions

@login_required
def profile(request, username=None):
    # Fetch the user, default to the logged-in user
    if username:
        user = get_object_or_404(CustomUser, username=username)
    else:
        user = request.user

    # Ensure the profile exists for the user
    profile, created = Profile.objects.get_or_create(user=user)
    # Fetch content authored by the user
    user_content = Content.objects.filter(author=user)  # Assuming ForeignKey to CustomUser in Content model
    # Fetch books authored by the user
    books_with_user_content = Book.objects.filter(author=user)  # Assuming ForeignKey to CustomUser in Book model
    # Fetch books purchased by the user
    purchased_books = Purchase.objects.filter(user=user)  # Assuming ForeignKey to CustomUser in Purchase model
    # Check if the profile being viewed belongs to the logged-in user
    is_self = request.user == user
    context = {
        'profile': profile,
        'user_content': user_content,
        'books_with_user_content': books_with_user_content,
        'purchased_books': purchased_books,
        'is_self': is_self,
    }
    return render(request, 'users/profile.html', context)

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(CustomUser, username=username)
    if request.user != user_to_follow:
        request.user.follow(user_to_follow)
        create_follow_notification(request.user, user_to_follow)  # Call the notification function
    return redirect('profile', username=username)

@login_required
def send_message(request, username):
    receiver = get_object_or_404(CustomUser, username=username)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            return redirect('users:profile_with_username', username=username)
    else:
        form = MessageForm()

    return render(request, 'users/send_message.html', {'form': form, 'receiver': receiver})

@login_required
def inbox(request):
    messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'users/inbox.html', {'messages': messages})

@login_required
def user_settings(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        # Handle form submission for user settings
        # For example, updating bio or profile picture
        pass
    
    context = {
        'profile': profile
    }
    return render(request, 'users/user_settings.html', context)

@login_required
def user_likes(request):
    user = request.user
    likes = user.likes.all()

    context = {
        'likes': likes
    }
    return render(request, 'users/user_likes.html', context)

@login_required
def user_followers(request):
    user = request.user
    followers = user.followers.all()

    context = {
        'followers': followers
    }
    return render(request, 'users/user_followers.html', context)

@login_required
def user_following(request, username):
    user = get_object_or_404(CustomUser, username=username)
    following = user.following.all()
    context = {
        'user': user,
        'following': following,
    }
    return render(request, 'users/user_following.html', context)

@login_required
def edit_profile(request):
    profile = request.user.profile  # Get the user's profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('users:profile')  # Redirect to profile page after saving
    else:
        form = ProfileForm(instance=profile)

    context = {
        'form': form,
    }
    return render(request, 'users/edit_profile.html', context)

@login_required
def inbox(request):
    messages = Message.objects.filter(recipient=request.user)
    return render(request, 'users/inbox.html', {'messages': messages})

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(CustomUser, username=username)
    if request.user != user_to_follow:
        request.user.follow(user_to_follow)
        create_follow_notification(request.user, user_to_follow)  # Call the notification function
    return redirect('users:profile_with_username', username=username)

def unfollow_user(request, username):
    # Get the user to unfollow
    user_to_unfollow = get_object_or_404(CustomUser, username=username)
    
    # Check if the user is trying to unfollow themselves
    if request.user != user_to_unfollow:
        # Remove the follow action here
        request.user.unfollow(user_to_unfollow)  # Assuming `unfollow` is a method on CustomUser
        # Optionally, create a notification for the unfollow action
        create_unfollow_notification(request.user, user_to_unfollow)
    
    # Redirect to the profile of the user who was unfollowed
    return redirect('users:profile', username=username)

def create_unfollow_notification(unfollower, unfollowed_user):
    Notification.objects.create(
        user=unfollowed_user,
        message=f'{unfollower.username} stopped following you.'
    )

@login_required
def message_user(request, username):
    recipient = get_object_or_404(CustomUser, username=username)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()
            create_message_notification(request.user, recipient)  # Call the notification function
            return redirect('users:message_user', username=username)
    else:
        form = MessageForm()

    messages = Message.objects.filter(
        sender=request.user, recipient=recipient
    ) | Message.objects.filter(
        sender=recipient, recipient=request.user
    ).order_by('timestamp')

    return render(request, 'users:message_user.html', {'form': form, 'messages': messages, 'recipient': recipient})

# When a new message is created:
def create_message_notification(sender, recipient):
    Notification.objects.create(
        user=recipient,
        message=f'{sender.username} sent you a message.'
    )
    
@login_required
def view_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    return render(request, 'users:notifications.html', {'notifications': notifications})

def create_follow_notification(follower, followed_user):
    Notification.objects.create(
        user=followed_user,
        message=f'{follower.username} started following you.'
    )

@login_required
def update_notifications(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = NotificationSettingsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('update_notifications')
    else:
        form = NotificationSettingsForm(instance=profile)
    return render(request, 'users/update_notifications.html', {'form': form})

@login_required
def update_privacy(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = PrivacySettingsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('update_privacy')
    else:
        form = PrivacySettingsForm(instance=profile)
    return render(request, 'users/update_privacy.html', {'form': form})

def follow_unfollow_view(request, user_id):
    target_user = CustomUser.objects.get(id=user_id)

    if request.user in target_user.followers.all():
        # Unfollow logic
        target_user.followers.remove(request.user)
    else:
        # Follow logic
        target_user.followers.add(request.user)

    return redirect('users:profile', user_id=user_id)

@login_required
def manage_payment_methods(request):
    payment_methods = PaymentMethod.objects.filter(user=request.user)
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment_method = form.save(commit=False)
            payment_method.user = request.user
            payment_method.save()
            return redirect('users:manage_payment_methods')
    else:
        form = PaymentMethodForm()
    return render(request, 'users/manage_payment_methods.html', {
        'form': form,
        'payment_methods': payment_methods
    })

