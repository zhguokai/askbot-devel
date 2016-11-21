import sys
from django.core.management.base import NoArgsCommand
from askbot import models
from askbot import forms
from askbot.utils import console
from askbot.models import signals
from askbot.conf import settings as askbot_settings
from django.utils.translation import activate

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        signal_data = signals.pop_all_db_signal_receivers()
        self.run_command()
        signals.set_all_db_signal_receivers(signal_data)

    def run_command(self):
        """method that runs the actual command"""
        #go through tags and find character case duplicates and eliminate them
        activate('en')
        tagnames = models.Tag.objects.values_list('name', flat = True)
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
            if askbot_settings.FORCE_LOWERCASE_TAGS:
                lowercased_name = first_tag.name.lower()
                if first_tag.name != lowercased_name:
                    print 'Converting tag %s to lower case' % first_tag.name
                    first_tag.name = lowercased_name
                    first_tag.save()

        #go through questions and fix tag records on each
        threads = models.Thread.objects.all()
        checked_count = 0
        found_count = 0
        total_count = threads.count()
        print "Searching for questions with inconsistent tag records:",
        for thread in threads:
            tags = thread.tags.all()
            denorm_tag_set = set(thread.get_tag_names())
            norm_tag_set = set(thread.tags.values_list('name', flat=True))
            if norm_tag_set != denorm_tag_set:

                if thread.last_activity_by:
                    user = thread.last_activity_by
                    timestamp = thread.last_activity_at
                else:
                    user = thread.author
                    timestamp = thread.added_at

                split_tags = thread.tagnames.split()
                clean_tagnames = set()
                for tagname in split_tags:
                    try:
                        clean_tagname = forms.TagNamesField().clean(tagname)
                        clean_tagnames.add(clean_tagname)
                    except:
                        pass

                tagnames = ' '.join(list(clean_tagnames))

                thread.update_tags(
                    tagnames=tagnames,
                    user=user,
                    timestamp=timestamp
                )
                thread.tagnames = tagnames
                thread.save()
                found_count += 1

            checked_count += 1
            console.print_progress(checked_count, total_count)
        console.print_progress(checked_count, total_count)

        #update tag used counts
        print '\nFixing tag use counts ...',
        total_count = models.Tag.objects.count()
        checked_count = 0
        for tag in models.Tag.objects.all().iterator():
            tag.update_used_counts()
            checked_count += 1
            console.print_progress(checked_count, total_count)
        console.print_progress(checked_count, total_count)

        print '\n'

        if found_count:
            print '%d problem questions found, tag records restored' % found_count
        else:
            print 'Did not find any problems'
