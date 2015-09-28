from django.apps import appconfig
class AskbotConfig(AppConfig):
    name = 'Askbot'
    verbose_name = 'Askbot Q&A platform'

    def ready(self):
        import followit
        user_model = self.get_model('askbot.User')
        followit.register(user_model)
