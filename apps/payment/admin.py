from django.contrib import admin

from . import models

admin.site.register(models.TicketTransaction)
admin.site.register(models.OrganizationAccounting)
admin.site.register(models.CommissionRules)
