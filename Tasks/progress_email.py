# BackEnd/Tasks/progress_email.py
from celery import shared_task
from BackEnd.Utils.email import send_progress_report
from BackEnd.Routes.analytics import get_feedback_analytics


@shared_task
def send_monthly_report():
    db = get_db()
    users = db.query(User).all()

    for user in users:
        analytics = get_feedback_analytics(db, user.id)
        send_progress_report(user.email, analytics)


# Schedule monthly reports
celery_app.conf.beat_schedule = {
    "monthly-report": {
        "task": "BackEnd.Tasks.progress_email.send_monthly_report",
        "schedule": crontab(day_of_month="1")
    }
}