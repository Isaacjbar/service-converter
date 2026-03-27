from django.contrib import admin
from .models import DiagramHistory

@admin.register(DiagramHistory)
class DiagramHistoryAdmin(admin.ModelAdmin):
    list_display = ['filename', 'user', 'version', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['filename']
