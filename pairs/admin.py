from django.contrib import admin

from .models import Pair, PairInvitation


@admin.register(Pair)
class PairAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "one",
        "two",
        "active",
        "created_at",
        "updated_at",
    )
    list_filter = ("active", "created_at")
    search_fields = (
        "one__email",
        "one__username",
        "two__email",
        "two__username",
    )
    autocomplete_fields = ("one", "two")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(PairInvitation)
class PairInvitationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "inviter",
        "invited_email",
        "invitee",
        "pair",
        "accepted_at",
        "active",
        "created_at",
    )
    list_filter = ("active", "accepted_at", "created_at")
    search_fields = (
        "invited_email",
        "inviter__email",
        "inviter__username",
        "invitee__email",
        "invitee__username",
        "token",
    )
    autocomplete_fields = ("inviter", "invitee", "pair")
    readonly_fields = ("id", "token", "created_at", "updated_at", "accepted_at")
    ordering = ("-created_at",)
