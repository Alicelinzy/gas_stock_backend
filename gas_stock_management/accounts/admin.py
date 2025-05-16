from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address', 'is_verified', 'created_at', 'updated_at')
    search_fields = ('user__username', 'phone_number', 'address')
    list_filter = ('is_verified', 'created_at')
