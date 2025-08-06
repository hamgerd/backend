from rest_framework import serializers

from apps.core.serializers import GeoLocationSerializer

from .models import Organization, OrganizationSocialLink


class OrganizationSocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSocialLink
        fields = ["platform", "url"]


class OrganizationSerializer(serializers.ModelSerializer):
    social_links = OrganizationSocialLinkSerializer(required=False, many=True)

    class Meta:
        model = Organization
        fields = [
            "public_id",
            "name",
            "username",
            "logo",
            "description",
            "email",
            "address",
            "website",
            "event_count",
            "geo_location",
            "social_links",
        ]
        read_only_fields = ["event_count", "public_id"]


class OrganizationCreateSerializer(serializers.ModelSerializer):
    geo_location = GeoLocationSerializer(required=False, allow_null=True)
    social_links = OrganizationSocialLinkSerializer(required=False, many=True)

    def update(self, instance, validated_data):
        social_links_data = validated_data.pop("social_links", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        instance.social_links.all().delete()
        for social_link_data in social_links_data:
            OrganizationSocialLink.objects.create(organization=instance, **social_link_data)

        return instance

    def create(self, validated_data):
        social_links_data = validated_data.pop("social_links", [])
        organization = Organization.objects.create(**validated_data)
        for social_link_data in social_links_data:
            OrganizationSocialLink.objects.create(organization=organization, **social_link_data)
        return organization

    class Meta:
        model = Organization
        fields = [
            "name",
            "username",
            "logo",
            "description",
            "email",
            "address",
            "website",
            "geo_location",
            "social_links",
        ]
