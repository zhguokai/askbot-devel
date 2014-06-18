from django.contrib.auth.models import Group
from askbot.management.commands.base import MergeRelationsCommand

class Command(MergeRelationsCommand):

    model = Group
    print_warnings = True

    def cleanup(self):
        """save 'to' user and delete the 'from' one"""
        self.to_object.save()
        self.from_object.delete()
