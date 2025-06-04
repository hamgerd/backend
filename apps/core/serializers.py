from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(read_only=True)

    class Meta:
        fields = ["public_id"]
        extra_kwargs = {"public_id": {"read_only": True}}
