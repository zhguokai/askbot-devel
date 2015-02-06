"""Recounts user's badges"""
from askbot import const
from askbot.models import (Award, User)
from askbot.utils.console import ProgressBar
from django.core.management.base import NoArgsCommand
from django.db.models import Count

class Command(NoArgsCommand):
    def handle_noargs(self, *args, **kwargs):
        users = User.objects.all()
        count = users.count()
        msg = 'Counting user badges'
        for user in ProgressBar(users.iterator(), count, msg):
            self.recount_badges(user)

    @classmethod
    def recount_badges(cls, user):
        bronze, silver, gold = 0, 0, 0

        awards = Award.objects.filter(
                                user=user
                            ).annotate(
                                count=Count('badge')
                            )
        for award in awards:
            badge = award.badge
            if badge.is_enabled():
                level = badge.get_level()
                if level == const.BRONZE_BADGE:
                    bronze += award.count
                elif level == const.SILVER_BADGE:
                    silver += award.count
                elif level == const.GOLD_BADGE:
                    gold += award.count

        user.bronze = bronze
        user.silver = silver
        user.gold = gold
        user.save()

