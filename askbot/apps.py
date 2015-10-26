from django.apps import AppConfig
from django.contrib.auth import get_user_model

class AskbotConfig(AppConfig):
    name = 'askbot'
    verbose_name = 'Askbot Q&A platform'

    def ready(self):
        from askbot.models import badges
        try:
            badges.init_badges()
        except:
            pass

        import followit
        user_model = get_user_model()
        followit.register(user_model)
