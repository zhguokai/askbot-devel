from django.core.management.base import CommandError
from django.db import transaction
from askbot.models import User
from askbot.management.commands.base import MergeRelationsCommand

class Command(MergeRelationsCommand):

    model = User
    print_warnings = False

    def process_fields(self):
        """add reputations, badge counts and important dates"""
        self.to_object.reputation += self.from_object.reputation - 1
        self.to_object.gold += self.from_object.gold
        self.to_object.silver += self.from_object.silver
        self.to_object.bronze += self.from_object.bronze

        if self.from_object.last_seen > self.to_object.last_seen:
            self.to_object.last_seen = self.from_object.last_seen

        if self.from_object.date_joined < self.to_object.date_joined:
            self.to_object.date_joined = self.from_object.date_joined

    def cleanup(self):
        """save 'to' user and delete the 'from' one"""
        self.to_object.save()
        self.from_object.delete()
