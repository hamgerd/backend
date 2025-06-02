# Register your models here.
from django.contrib import admin

from .models import Event, EventCategory, Ticket, TicketType

admin.site.register(Event)
admin.site.register(EventCategory)
admin.site.register(Ticket)
admin.site.register(TicketType)
