from django.db.models import signals as django_signals
from django.contrib.auth.models import User

from haystack.signals import BaseSignalProcessor

class AskbotRealtimeSignalProcessor(BaseSignalProcessor):
    '''
    Based on haystack RealTimeSignalProcessor with some
    modifications to work with askbot soft-delete models
    '''

    def setup(self):
        django_signals.post_save.connect(self.handle_save)
        django_signals.post_delete.connect(self.handle_delete, sender=User)

        try:
            from askbot.models import signals as askbot_signals
            askbot_signals.delete_question_or_answer.connect(self.handle_delete)
        except ImportError:
            pass

    def teardown(self):
        django_signals.post_save.disconnect(self.handle_save)
        django_signals.post_delete.disconnect(self.handle_delete)
        #askbot signals
        try:
            from askbot.models import signals as askbot_signals
            askbot_signals.delete_question_or_answer.disconnect(self.handle_delete)
        except ImportError:
            pass
