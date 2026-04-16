from django.urls import path

from .views import PairInvitationAcceptView, PairInviteView

app_name = "pairs"

urlpatterns = [
    path("pairs/convidar/", PairInviteView.as_view(), name="invite"),
    path(
        "pairs/convites/aceitar/<uuid:token>/",
        PairInvitationAcceptView.as_view(),
        name="invite_accept",
    ),
]
