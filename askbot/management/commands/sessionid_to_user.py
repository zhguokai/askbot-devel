from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import Session
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    args = '<sessionid>'
    help = "Get User identifiers for supplied sessionid"

    def handle(self, *args, **kwargs):
        sessionid = args[0]
        sessiondict = Session.objects.get(session_key=sessionid).get_decoded()
        userid = sessiondict['_auth_user_id']
        user = User.objects.get(id=userid)
        self.stdout.write("The User is '%s' (with ID '%s', and email '%s').\n" % (
            user.username,
            userid,
            user.email))
