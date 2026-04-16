from django.db import DatabaseError
from django.db.models import Q
from django.db.models.functions import TruncDate
from django.utils import timezone


def navbar_pair_context(request):
    show_invite_my_love = False
    show_daily_report = False

    if request.user.is_authenticated:
        try:
            from pairs.models import Pair

            has_pair = Pair.objects.filter(
                Q(one=request.user) | Q(two=request.user),
                active=True,
            ).exists()
            has_report_today = False
            if has_pair:
                from reports.models import DailyReport

                current_tz = timezone.get_current_timezone()
                has_report_today = (
                    DailyReport.objects.filter(
                        reporter=request.user,
                        active=True,
                    )
                    .annotate(local_created_date=TruncDate("created_at", tzinfo=current_tz))
                    .filter(local_created_date=timezone.localdate())
                    .exists()
                )
            show_invite_my_love = not has_pair
            show_daily_report = has_pair and not has_report_today
        except DatabaseError:
            # During initial setup/migrations, table may not exist yet.
            show_invite_my_love = False
            show_daily_report = False

    return {
        "show_invite_my_love": show_invite_my_love,
        "show_daily_report": show_daily_report,
    }
