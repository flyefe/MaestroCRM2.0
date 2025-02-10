from django.contrib import admin
from .models import Contact, Log

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'assigned_staff', 'phone_number', 'traffic_source', 'services', 'created_at', 'modified_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number', 'tags')

    # def google_drive_link_display(self, obj):
    #     if obj.google_drive_link:
    #         return format_html('<a href="{}" target="_blank">Drive Folder</a>', obj.google_drive_link)
    #     return "No Link"

    # google_drive_link_display.short_description = "Google Drive"

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('contact', 'log_type', 'log_title', 'created_by', 'created_at')
    search_fields = ('contact__user__username', 'log_title', 'log_type', 'created_by__username')


# @admin.register(Address)
# class AddressAdmin(admin.ModelAdmin):
#     list_display = ('first_line', 'second_line', 'city', 'state', 'country', 'postal_code')
#     search_fields = ('city', 'state', 'country', 'first_line')