from django.core.management.base import BaseCommand
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging

class Command(BaseCommand):
    help = 'Test SendGrid email connectivity'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Recipient email address')

    def handle(self, *args, **options):
        recipient = options['email']
        self.stdout.write(self.style.NOTICE(f"Attempting to send test email to {recipient}..."))

        api_key = getattr(settings, 'SENDGRID_API_KEY', '')
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '')

        if not api_key:
            self.stdout.write(self.style.ERROR("SENDGRID_API_KEY is not configured in settings."))
            return

        if not from_email:
            self.stdout.write(self.style.ERROR("DEFAULT_FROM_EMAIL is not configured in settings."))
            return

        # Diagnostic info
        key_len = len(api_key)
        self.stdout.write(f"Key metadata: length={key_len}, starts='{api_key[:4]}', ends='{api_key[-4:]}'")

        try:
            sg = SendGridAPIClient(api_key)
            message = Mail(
                from_email=from_email,
                to_emails=recipient,
                subject='SendGrid Connectivity Test - Django',
                plain_text_content='This is a test email from your Django application to verify SendGrid API key.'
            )
            response = sg.send(message)
            
            if 200 <= response.status_code < 300:
                self.stdout.write(self.style.SUCCESS(f"Successfully sent test email! Status code: {response.status_code}"))
            else:
                self.stdout.write(self.style.ERROR(f"SendGrid rejected the request. Status code: {response.status_code}"))
                self.stdout.write(f"Response body: {response.body}")
                self.stdout.write(f"Response headers: {response.headers}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while sending email: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())
