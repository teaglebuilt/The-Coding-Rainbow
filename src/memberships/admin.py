from django.contrib import admin
from .models import Membership, UserMembership, Subscription, FriendRequest


admin.site.register(Membership)
admin.site.register(UserMembership)
admin.site.register(Subscription)
admin.site.register(FriendRequest)

# Register your models here.
