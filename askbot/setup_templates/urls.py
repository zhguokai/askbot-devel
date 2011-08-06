"""
main url configuration file for the askbot site
"""
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

handler500 = 'askbot.views.meta.server_error'
handler404 = 'askbot.views.meta.page_not_found'

urlpatterns = patterns('',
    (r'%s' % settings.ASKBOT_URL, include('askbot.urls')),
    (r'^admin/', include(admin.site.urls)),
    #(r'^cache/', include('keyedcache.urls')), - broken views disable for now
    (r'^settings/', include('askbot.deps.livesettings.urls')),
    (r'^robots.txt$', include('robots.urls')),
)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
                    url(r'^rosetta/', include('rosetta.urls')),
                )
