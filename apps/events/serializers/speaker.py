from rest_framework import serializers

from apps.events.models import Speaker


class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ["id", "name", "image", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
