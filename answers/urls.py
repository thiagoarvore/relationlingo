from django.urls import path

from .views import AnswerCreateView

app_name = "answers"

urlpatterns = [
    path(
        "answers/relatorios/<uuid:report_id>/responder/",
        AnswerCreateView.as_view(),
        name="create",
    ),
]
