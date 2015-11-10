from askbot.deps.django_authopenid.protocols.base import BaseProtocol
from askbot.conf import settings as askbot_settings
from cas import CASClient

class CASLoginProvider(BaseProtocol):

    def __init__(self, success_redirect_url=None):
        self.name = 'cas'
        self.display_name = 'CAS'
        self.icon_media_path = askbot_settings.CAS_LOGIN_BUTTON
        self.client = CASClient(
                                version=askbot_settings.CAS_PROTOCOL_VERSION,
                                server_url=askbot_settings.CAS_SERVER_URL,
                                service_url=success_redirect_url
                               )

    def verify_token(self, *args, **kwargs):
        return self.client.verify_token(*args, **kwargs)

    def get_login_url(self):
        return self.client.get_login_url()
