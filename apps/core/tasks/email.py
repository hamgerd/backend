from celery import shared_task
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string


@shared_task
def send_email(
    subject,
    from_email,
    recipient_list,
    message=None,
    template_name=None,
    context=None,
    fail_silently=False,
    auth_user=None,
    auth_password=None,
    connection=None,
    html_message=None,
):
    """
    Celery task to send email
    """

    if template_name is None and message is None:
        raise ValueError("Either message or template_name should be provided")

    if template_name:
        html_content = render_to_string(template_name, context)
        email = EmailMessage(subject, html_content, from_email, recipient_list)
        email.content_subtype = "html"
        return email.send()

    return send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=fail_silently,
        auth_user=auth_user,
        auth_password=auth_password,
        connection=connection,
        html_message=html_message,
    )
