import re
import sys
from django.core.management.base import NoArgsCommand
from django.conf import settings as django_settings
from django.db import transaction
from django.utils import translation
from askbot import const
from askbot import models
from askbot import forms
from askbot.utils import console
from askbot.models import signals
from askbot.conf import settings as askbot_settings
from askbot.management.commands.rename_tags import get_admin

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        signal_data = signals.pop_all_db_signal_receivers()
        self.run_command()
        signals.set_all_db_signal_receivers(signal_data)

    @transaction.commit_manually
    def run_command(self):
        """method that runs the actual command"""
        #go through tags and find character case duplicates and eliminate them
        translation.activate(django_settings.LANGUAGE_CODE)
        tagnames = models.Tag.objects.values_list('name', flat = True)
        admin = get_admin()
        #1) first we go through all tags and
        #either fix or delete illegal tags
        found_count = 0
        for name in tagnames:
            dupes = models.Tag.objects.filter(name__iexact = name)
            first_tag = dupes[0]
            if dupes.count() > 1:
                line = 'Found duplicate tags for %s: ' % first_tag.name
                print line,
                for idx in xrange(1, dupes.count()):
                    print dupes[idx].name + ' ',
                    dupes[idx].delete()
                print ''
            #todo: see if we can use the tag "clean" procedure here
            if askbot_settings.FORCE_LOWERCASE_TAGS:
                lowercased_name = first_tag.name.lower()
                if first_tag.name != lowercased_name:
                    print 'Converting tag %s to lower case' % first_tag.name
                    first_tag.name = lowercased_name
                    first_tag.save()

            #if tag name starts with forbidden character, chop off that character
            #until no more forbidden chars are at the beginning
            #if the tag after chopping is zero length, delete the tag
            first_char_regex = re.compile('^%s+' % const.TAG_FORBIDDEN_FIRST_CHARS)

            old_name = first_tag.name
            new_name = first_char_regex.sub('', first_tag.name)
            if new_name == old_name:
                continue
            else:
                first_tag.name = new_name

            if len(first_tag.name) == 0:
                #the tag had only bad characters at the beginning
                first_tag.delete()
                found_count += 1
            else:
                #save renamed tag if there is no exact match
                new_dupes = models.Tag.objects.filter(name__iexact=first_tag.name)
                if new_dupes.count() == 0:
                    first_tag.save()
                else:
                    #we stripped forbidden chars and have a tag with duplicates.
                    #Now we need to find all questions with the existing tag and 
                    #reassign those questions to other tag
                    to_tag = new_dupes[0].name
                    from_tag = first_tag
                    threads = models.Thread.objects.filter(tags=from_tag)
                    for thread in threads:
                        tagnames = set(thread.get_tag_names())
                        tagnames.remove(old_name)
                        tagnames.add(to_tag)
                        admin.retag_question(
                            question=thread._question_post(),
                            tags=' '.join(tagnames)
                        )
                    first_tag.delete()
                    found_count += 1
                
        transaction.commit()

        #2) go through questions and fix tag records on each
        # and recalculate all the denormalised tag names on threads
        threads = models.Thread.objects.all()
        checked_count = 0
        total_count = threads.count()
        print "Searching for questions with inconsistent tag records:",
        for thread in threads:
            tags = thread.tags.all()
            denorm_tag_set = set(thread.get_tag_names())
            norm_tag_set = set(thread.tags.values_list('name', flat=True))
            if norm_tag_set != denorm_tag_set:
                admin.retag_question(
                    question=thread._question_post(),
                    tags=' '.join(norm_tag_set)
                )

            transaction.commit()
            checked_count += 1
            console.print_progress(checked_count, total_count)
        console.print_progress(checked_count, total_count)

        if found_count:
            print '%d problem questions found, tag records restored' % found_count
        else:
            print 'Did not find any problems'
