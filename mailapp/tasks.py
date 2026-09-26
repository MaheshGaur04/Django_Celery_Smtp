from celery import shared_task
from django.core.mail import EmailMultiAlternatives, send_mass_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_email_task(self, recipient_email, subject, message, html_content=None):
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email]
        )
        
        # Support HTML email templates
        if html_content:
            email.attach_alternative(html_content, "text/html")
            
        email.send()
        logger.info(f"Successfully sent email to {recipient_email}")
        return f"Success: Email sent to {recipient_email}"
        
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        # Retry mechanism for temporary network/SMTP failures
        self.retry(exc=e, countdown=10)

@shared_task
def send_bulk_email_task(recipient_list, subject, message):
    try:
        messages = tuple(
            (subject, message, settings.DEFAULT_FROM_EMAIL, [recipient]) 
            for recipient in recipient_list
        )
        send_mass_mail(messages, fail_silently=False)
        logger.info(f"Successfully sent bulk emails to {len(recipient_list)} recipients")
        return f"Success: Bulk email sent to {len(recipient_list)} addresses"
        
    except Exception as e:
        logger.error(f"Failed bulk email dispatch: {str(e)}")
        return str(e)