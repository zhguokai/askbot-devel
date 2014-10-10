from askbot.models import Feed
from askbot.models import Space
from askbot.models import Thread
from askbot.utils.console import ProgressBar
from django.conf import settings as django_settings
from django.core.management.base import NoArgsCommand
from django.contrib.sites.models import Site

"""
Set up a new sub-site http://sitename.main-domain
========================================
This command sets up the necessary objects and relationships for a new askbot
sub-site (eg. http://sitename.domain). However, there are some other steps
that you must take as well. These are detailed below:

* note the id of the Group that's going to be the sub-site's default ask Group,
    creating one via the web UI if necessary. If you create a Group, consider 
    adding an admin/mod user to it so that there's someone to cover the 
    moderation queue for that Group.
* for each of the following tables, determine what the next free id is as
    this will be the id of the corresponding object created by this command
    * Site
    * Space
    * Feed
* now modify the settings.py file as follows (if site_id is 10, "|<site_id>|" 
    means you should use "|10|"):
    * add the new sub-site's domain (sitename.main-domain) to the ALLOWED_HOSTS list
    * add the id for the new Site object to ASKBOT_SITE_IDS
    * add the id for the new Site object to ASKBOT_PARTNER_SITE_IDS (so that the new site
        will appear in "Post at partner sites" list)
    * add this to the ASKBOT_SITES dict: 
        * <site_id>: ('<site_name>', '<site_domain>')
    * add this to the ASKBOT_SPACES dict: 
        * <space_id>: ('<space_name>', '<group_id>')
    * add this to the ASKBOT_FEEDS dict: 
        * <feed_id>: ('<feed_name>', <site_id>, <space_ids>)
        * where <space_ids> is a list of Space ids, the first one being the primary
    * add this to the ASKBOT_SITE_TO_DEFAULT_ASK_GROUP:
        * <site_id>: <group_id>
* run this managment command to create the objects and their relationships:
    * python manage.py askbot_setup_sites --settings=kp_settings
* create <site_name>_settings.py file that imports * from the main settings 
    module and then sets:
    * SITE_ID
    * ASKBOT_EXTRA_SKINS_DIR
    * STATICFILES_DIRS += (ASKBOT_EXTRA_SKINS_DIR,)
    * DEBUG
    * DEFAULT_ASK_GROUP_ID
    * ASKBOT_LANGUAGE_MODE ('single-lang' or 'user-lang')
    * LIVESETTINGS_OPTIONS
* prepare an askbot livesettings module (you can base it on one you've extracted 
    from your main Site at maindomain/settings/export/ - remember to change the key 
    for the top-level dictionary to your new Site's id! Assign the entire dictionary 
    to the variable name 'settings' and give the file a .py extension)
* load the livesettings for your new site:
    * python manage.py askbot_import_livesettings --settings=<site_name>_settings settings_import
* add the following new line to your cronjob shell script to ensure you'll be sending
    out daily/weekly digest emails about updates in the new sub-site:
    * python manage.py send_email_alerts --settings=<site_name>_settings
* finally, reconfigure your webserver of choice as appropriate
"""

SITES = getattr(django_settings, 'ASKBOT_SITES')
SPACES = getattr(django_settings, 'ASKBOT_SPACES')
FEEDS = getattr(django_settings, 'ASKBOT_FEEDS')

def get_object_by_id(object_class, object_id):
    try:
        return object_class.objects.get(id=object_id)
    except object_class.DoesNotExist:
        return object_class(id=object_id)

class Command(NoArgsCommand):
    def handle_noargs(self, **kwargs):

        #create spaces
        for (space_id, space_settings) in SPACES.items():
            space = get_object_by_id(Space, space_id)
            space.name = space_settings[0]
            space.save()
            
        #create sites
        for (site_id, site_data) in SITES.items():
            site = get_object_by_id(Site, site_id)
            site.name = site_data[0]
            site.domain = site_data[1]
            site.save()

        #create feeds
        for (feed_id, feed_data) in FEEDS.items():
            feed = get_object_by_id(Feed, feed_id)
            feed.name = feed_data[0]
            site_id = feed_data[1]
            space_ids = feed_data[2]
            feed.default_space = get_object_by_id(Space, space_ids[0])
            feed.site = get_object_by_id(Site, site_id)
            feed.save()

            for space_id in space_ids:
                space = get_object_by_id(Space, space_id)
                feed.add_space(space)

        #get site with lowest id:
        main_site = Site.objects.all().order_by('id')[0]
        #naive way to get the main feed for the site
        main_feed = Feed.objects.filter(
                                site=main_site
                            ).order_by('id')[0]

        threads = Thread.objects.all()
        count = threads.count()
        message = 'Adding all threads to the %s space' % main_site.name

        main_space = main_feed.default_space
        for thread in ProgressBar(threads.iterator(), count, message):
            main_space.questions.add(thread)
