from django.apps import AppConfig
from django.contrib.auth import get_user_model

class AskbotConfig(AppConfig):
    name = 'askbot'
    verbose_name = 'Askbot Q&A platform'

    def ready(self):
        import followit
        user_model = get_user_model()
        followit.register(user_model)
