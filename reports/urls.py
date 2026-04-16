from django.urls import path

from .views import (
    DailyReportAboutMeListView,
    DailyReportCreateView,
    DailyReportDetailView,
    DailyReportListView,
)

app_name = "reports"

urlpatterns = [
    path("reports/", DailyReportListView.as_view(), name="list"),
    path("reports/<uuid:report_id>/", DailyReportDetailView.as_view(), name="detail"),
    path("reports/sobre-mim/", DailyReportAboutMeListView.as_view(), name="about_me"),
    path("reports/novo/", DailyReportCreateView.as_view(), name="create"),
]
