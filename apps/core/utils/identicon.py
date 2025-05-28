import hashlib
from io import BytesIO

from identiconify import PilIdenticon


def add_profile_picture(instance, username_field="username", profile_picture_field="profile_picture"):
    """
    Utility function to generate and add identicon profile picture for a model instance.

    Args:
        instance: The model instance to add a profile picture to
        username_field: The name of the field containing the username
        profile_picture_field: The name of the field for the profile picture
    """
    username = getattr(instance, username_field)
    profile_picture = getattr(instance, profile_picture_field)

    identicon = PilIdenticon().generate(username)
    buffer = BytesIO()
    identicon.save(buffer, format="PNG")
    buffer.seek(0)

    profile_picture.save(f"{hashlib.md5(username.encode()).hexdigest()}.png", buffer, save=False)
