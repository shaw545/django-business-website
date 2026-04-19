from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'service_interest', 'created_at')
    search_fields = ('name', 'email', 'company', 'message')
    list_filter = ('service_interest', 'created_at')