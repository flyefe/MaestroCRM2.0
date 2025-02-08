# emails/email_utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_custom_email(subject, recipient_list, template_name, context):
    """
    Sends an email using a specified template and context.

    :param subject: Email subject
    :param recipient_list: List of email recipients
    :param template_name: Path to the email template
    :param context: Context dictionary for rendering the template
    """
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)  # Strip HTML tags for plain text version
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
