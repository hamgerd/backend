from celery import shared_task
from django.utils import timezone

from .models import Event


@shared_task
def end_up_events_on_end_date():
    finished_event_list = Event.objects.filter(end_date__lt=timezone.now())
    for event in finished_event_list:
        event.end_up()
