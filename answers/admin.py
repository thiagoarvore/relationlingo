from django.contrib import admin

from .models import Answer


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("created_at", "report", "active")
    search_fields = ("text", "report__reporter__email", "report__subject__email")
    readonly_fields = ("id", "created_at", "updated_at")
