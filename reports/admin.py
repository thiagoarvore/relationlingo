from django.contrib import admin

from .models import DailyReport


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ("created_at", "reporter", "subject", "critic_level", "active")
    list_filter = ("critic_level", "active", "created_at")
    search_fields = (
        "reporter__email",
        "reporter__username",
        "subject__email",
        "subject__username",
        "critic",
        "compliment",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "reporter",
        "subject",
        "critic",
        "critic_level",
        "compliment",
        "active",
    )

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
