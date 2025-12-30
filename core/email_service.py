import threading
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import EmailLog

class EmailThread(threading.Thread):
    """
    Background Thread to send email without blocking the API response.
    """
    def __init__(self, subject, recipient_list, html_content, text_content):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.text_content = text_content
        threading.Thread.__init__(self)

    def run(self):
        try:
            msg = EmailMultiAlternatives(
                subject=self.subject,
                body=self.text_content, # Plain text fallback
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=self.recipient_list
            )
            msg.attach_alternative(self.html_content, "text/html")
            msg.send()
            
            # Log Success
            EmailLog.objects.create(
                recipient=self.recipient_list[0],
                subject=self.subject,
                body=self.text_content,
                status='sent'
            )
        except Exception as e:
            # Log Failure
            EmailLog.objects.create(
                recipient=self.recipient_list[0],
                subject=self.subject,
                body=str(e),
                status='failed',
                error_message=str(e)
            )

class EmailService:
    @staticmethod
    def send_welcome_email(user):
        """
        Prepares the welcome email and dispatches it in the background.
        """
        subject = "Welcome to Django Store!"
        
        # Render HTML template
        context = {'username': user.username}
        html_content = render_to_string('emails/welcome.html', context)
        text_content = f"Welcome {user.username}! Thank you for joining Django Store."

        # Dispatch via Thread
        EmailThread(
            subject=subject,
            recipient_list=[user.email],
            html_content=html_content,
            text_content=text_content
        ).start()