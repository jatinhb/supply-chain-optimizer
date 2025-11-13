"""Admin configuration for accounts app."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'role', 'department', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'department', 'phone', 'avatar')}),
        ('Notifications', {'fields': ('notification_email', 'notification_alerts')}),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'resource_type', 'timestamp']
    list_filter = ['action', 'resource_type', 'timestamp']
    search_fields = ['user__email', 'resource_type', 'resource_id']
    readonly_fields = ['user', 'action', 'resource_type', 'resource_id',
                       'details', 'ip_address', 'user_agent', 'timestamp']
    ordering = ['-timestamp']
