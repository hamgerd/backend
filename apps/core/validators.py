from django.core.exceptions import ValidationError


def geo_location_validator(value):
    if value in [None, {}]:
        return None

    allowed_keys = {"latitude", "longitude", "zoom"}
    keys = set(value.keys())
    extra_keys = keys - allowed_keys
    missing_keys = allowed_keys - keys

    if extra_keys:
        raise ValidationError("Geo location contains extra keys: {}".format(", ".join(extra_keys)))
    if missing_keys:
        raise ValidationError("Geo location is missing keys: {}".format(", ".join(missing_keys)))

    latitude = value["latitude"]
    longitude = value["longitude"]
    zoom = value["zoom"]
    if not isinstance(latitude, float | int) or not (-90 <= latitude <= 90):
        raise ValidationError("Latitude must be a number between -90 and 90.")
    if not isinstance(longitude, float | int) or not (-180 <= longitude <= 180):
        raise ValidationError("Longitude must be a number between -180 and 180.")
    if not isinstance(zoom, float | int) or not (0 <= zoom <= 22):
        raise ValidationError("Zoom must be a number between 0 and 22.")

    return None
