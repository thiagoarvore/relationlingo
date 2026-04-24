import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django_base_kit.models import BaseModel

user_model = settings.AUTH_USER_MODEL


class Pair(BaseModel):
    one = models.ForeignKey(
        user_model, on_delete=models.PROTECT, related_name="pairs_as_one"
    )
    two = models.ForeignKey(
        user_model, on_delete=models.PROTECT, related_name="pairs_as_two"
    )

    class Meta:
        verbose_name = "Par"
        verbose_name_plural = "Pares"


class PairInvitation(BaseModel):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    inviter = models.ForeignKey(
        user_model,
        on_delete=models.PROTECT,
        related_name="pair_invitations_sent",
    )
    invitee = models.ForeignKey(
        user_model,
        on_delete=models.PROTECT,
        related_name="pair_invitations_accepted",
        null=True,
        blank=True,
    )
    invited_email = models.EmailField(db_index=True)
    pair = models.ForeignKey(
        "pairs.Pair",
        on_delete=models.PROTECT,
        related_name="invitations",
        null=True,
        blank=True,
    )
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Convite de Par"
        verbose_name_plural = "Convites de Par"
        ordering = ["-created_at"]

    def mark_as_accepted(self, invitee_user, pair):
        self.invitee = invitee_user
        self.pair = pair
        self.accepted_at = timezone.now()
        self.save(update_fields=["invitee", "pair", "accepted_at", "updated_at"])

    @property
    def is_accepted(self):
        return self.accepted_at is not None
