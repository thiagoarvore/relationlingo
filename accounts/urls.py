from django.urls import path

from .views import PairUndoView, UserProfileUpdateView

app_name = "accounts"

urlpatterns = [
    path(
        "accounts/profile/edit/", UserProfileUpdateView.as_view(), name="profile_edit"
    ),
    path("accounts/profile/pair/desfazer/", PairUndoView.as_view(), name="pair_undo"),
]
