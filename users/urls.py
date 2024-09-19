from django.urls import path, re_path
from . import views 
from django.conf import settings
from django.conf.urls.static import static

app_name = 'users'

urlpatterns = [
    re_path(r'^profile(?:/(?P<username>[^/]+))?/$', views.profile, name='profile'),
    path('settings/', views.user_settings, name='user_settings'),
    path('likes/', views.user_likes, name='user_likes'),
    path('followers/', views.user_followers, name='user_followers'),
    path('following/<str:username>/', views.user_following, name='user_following'),
    path('profile/<str:username>/', views.profile, name='profile_with_username'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('message/<str:username>/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('message/<str:username>/', views.message_user, name='message_user'),
    path('notifications/', views.view_notifications, name='view_notifications'),
    path('notifications/', views.update_notifications, name='update_notifications'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path('privacy/', views.update_privacy, name='update_privacy'),
    path('payment-methods/', views.manage_payment_methods, name='manage_payment_methods'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
