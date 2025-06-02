from rest_framework import serializers

from apps.events.models import Speaker


class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ["public_id", "name", "image", "created_at", "updated_at"]
        read_only_fields = ["public_id", "created_at", "updated_at"]
