from django.contrib import admin
from .models import Segment

@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'modified_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('contacts',)
