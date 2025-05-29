import hashlib
from io import BytesIO

from identiconify import PilIdenticon


def add_default_image(instance, username_field_name="username", image_field_name="image"):
    """
    Utility function to generate and add identicon image for a model instance.

    Args:
        instance: The model instance to add an image to
        username_field_name: The name of the field containing the username
        image_field_name: The name of the field for the image
    """
    username = getattr(instance, username_field_name)
    image_field = getattr(instance, image_field_name)

    identicon = PilIdenticon().generate(username)
    buffer = BytesIO()
    identicon.save(buffer, format="PNG")
    buffer.seek(0)

    image_field.save(f"{hashlib.md5(username.encode()).hexdigest()}.png", buffer, save=False)
