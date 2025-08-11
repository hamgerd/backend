from django.db.models.enums import TextChoices


class PlatformChoices(TextChoices):
    TELEGRAM = "tg", "telegram"
    LINKEDIN = "in", "linkedin"
    INSTAGRAM = "ig", "instagram"
