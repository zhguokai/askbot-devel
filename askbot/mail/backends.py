from django.core.mail.backends.base import BaseEmailBackend

class DebuggingBackend(BaseEmailBackend):
    """just lists recipient email addresses"""
    def send_messages(self, messages):
        for message in messages:
            print '\n'.join(message.recipients())
