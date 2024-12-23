from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_email(subject, message=None, recipient_list=None, from_email=None, fail_silently=False, template_name=None, context=None):
    """
    Helper function to send an email with support for HTML templates.

    Args:
        subject (str): Subject of the email.
        message (str, optional): Plain-text body of the email. Defaults to None.
        recipient_list (list): List of recipient email addresses.
        from_email (str, optional): Sender email address. Defaults to settings.EMAIL_HOST_USER.
        fail_silently (bool, optional): Whether to suppress errors. Defaults to False.
        template_name (str, optional): Path to the HTML template. Defaults to None.
        context (dict, optional): Context variables for rendering the template. Defaults to None.

    Returns:
        int: The number of successfully delivered messages (can be 0 or more).
    """
    if not from_email:
        from_email = settings.EMAIL_HOST_USER
        # from_email = 'no-reply@realtruedate.com'

    # Render HTML content if a template is provided
    html_content = None
    if template_name and context:
        html_content = render_to_string(template_name, context)
        # Use plain text version if message is not provided
        if not message:
            from django.utils.html import strip_tags
            message = strip_tags(html_content)

    # Create the email message
    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=from_email,
        to=recipient_list
    )

    # Attach HTML content if available
    if html_content:
        email.attach_alternative(html_content, "text/html")

    return email.send(fail_silently=fail_silently)
