from django import forms
from .models import Profile, Message, PaymentMethod

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'date_of_birth', 'location']
        
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']

class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['notification_emails']

class PrivacySettingsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['privacy_level']

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['card_number', 'expiry_date', 'card_holder_name', 'is_default']