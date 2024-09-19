from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(PaymentMethod)