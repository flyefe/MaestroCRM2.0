from celery import shared_task
from .email_utils import send_custom_email

@shared_task
def send_bulk_emails(subject, recipient_list, template_name, context):
    """
    Send bulk emails asynchronously using Celery.

    :param subject: Email subject
    :param recipient_list: List of recipients
    :param template_name: Email template
    :param context: Context for rendering the email
    """
    for recipient in recipient_list:
        send_custom_email(subject, [recipient], template_name, context)
