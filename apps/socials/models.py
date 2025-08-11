from django.db import models

from apps.socials.choices import PlatformChoices


class AbstractSocialLink(models.Model):
    platform = models.CharField(max_length=10, choices=PlatformChoices.choices)
    url = models.URLField()

    class Meta:
        abstract = True
