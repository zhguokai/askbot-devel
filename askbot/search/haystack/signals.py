from django.db.models import signals as django_signals
from django.contrib.auth.models import User
from haystack.signals import BaseSignalProcessor
from askbot.models import signals as askbot_signals

class AskbotRealtimeSignalProcessor(BaseSignalProcessor):
    '''
    Based on haystack RealTimeSignalProcessor with some
    modifications to work with askbot soft-delete models
    '''

    def setup(self):
        try:
            from askbot.models import Post, Thread
            django_signals.post_save.connect(self.handle_save, sender=User)
            django_signals.post_save.connect(self.handle_save, sender=Thread)
            django_signals.post_save.connect(self.handle_save, sender=Post)

            django_signals.post_delete.connect(self.handle_delete, sender=User)
            #askbot signals
            askbot_signals.delete_question_or_answer.connect(self.handle_delete, sender=Post)
            askbot_signals.delete_question_or_answer.connect(self.handle_delete, sender=Thread)
        except:
            pass

    def teardown(self):
        from askbot.models import Post, Thread
        django_signals.post_save.disconnect(self.handle_save, sender=User)
        django_signals.post_save.disconnect(self.handle_save, sender=Post)
        django_signals.post_save.disconnect(self.handle_save, sender=Thread)
        django_signals.post_delete.disconnect(self.handle_delete, sender=User)
        #askbot signals
        askbot_signals.delete_question_or_answer.disconnect(self.handle_delete, sender=Thread)
        askbot_signals.delete_question_or_answer.disconnect(self.handle_delete, sender=Post)
