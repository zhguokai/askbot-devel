from django.conf import settings as django_settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from askbot.deps.livesettings import ConfigurationSettings, forms
from askbot.deps.livesettings import ImageValue
from askbot.deps.livesettings.overrides import get_overrides
from django.contrib import messages

import logging
import StringIO
import yaml

log = logging.getLogger('configuration.views')


def group_settings(request, group, template='livesettings/group_settings.html'):
    # Determine what set of settings this editor is used for

    use_db, overrides = get_overrides();

    mgr = ConfigurationSettings()

    settings = mgr[group]
    title = settings.name
    log.debug('title: %s', title)

    if use_db:
        # Create an editor customized for the current user
        #editor = forms.customized_editor(settings)

        if request.method == 'POST':
            # Populate the form with user-submitted data
            data = request.POST.copy()
            form = forms.SettingsEditor(data, request.FILES, settings=settings)
            if form.is_valid():
                for name, value in form.cleaned_data.items():
                    group, key, lang = name.split('__')
                    cfg = mgr.get_config(group, key)

                    if isinstance(cfg, ImageValue):
                        if request.FILES and name in request.FILES:
                            value = request.FILES[name]
                        else:
                            continue

                    try:
                        cfg.update(value, lang)
                        #message='Updated %s on %s' % (cfg.key, cfg.group.key)
                        #messages.success(request, message)
                        #the else if for the settings that are not updated.
                    except Exception, e:
                        log.critical(e)
                        request.user.message_set.create(message=e.message)

                return HttpResponseRedirect(request.path)
        else:
            # Leave the form populated with current setting values
            #form = editor()
            form = forms.SettingsEditor(settings=settings)
    else:
        form = None

    return render_to_response(template, {
        'all_super_groups': mgr.get_super_groups(),
        'title': title,
        'settings_group' : settings,
        'form': form,
        'use_db' : use_db
    }, context_instance=RequestContext(request))
group_settings = never_cache(staff_member_required(group_settings))

# Site-wide setting editor is identical, but without a group
# staff_member_required is implied, since it calls group_settings
def site_settings(request):
    mgr = ConfigurationSettings()
    default_group= mgr.groups()[0].key
    return HttpResponseRedirect(reverse('group_settings', args=[default_group]))
    #return group_settings(request, group=None, template='livesettings/site_settings.html')

def export_as_python(request):
    """Export site settings as a dictionary of dictionaries"""

    from askbot.deps.livesettings.models import Setting, LongSetting
    import pprint

    work = {}
    both = list(Setting.objects.all())
    both.extend(list(LongSetting.objects.all()))

    for s in both:
        if not work.has_key(s.site.id):
            work[s.site.id] = {}
        sitesettings = work[s.site.id]

        if not sitesettings.has_key(s.group):
            sitesettings[s.group] = {}
        sitegroup = sitesettings[s.group]

        sitegroup[s.key] = s.value

    pp = pprint.PrettyPrinter(indent=4)
    pretty = pp.pformat(work)

    return render_to_response('livesettings/text.txt', { 'text' : pretty }, mimetype='text/plain')


def export_as_yaml(request):
    from askbot.deps.livesettings.models import Setting, LongSetting

    settings = list(Setting.objects.all().values('group', 'key', 'value'))
    long_settings = list(LongSetting.objects.all().values('group', 'key', 'value'))
    result = dump_yaml(settings + long_settings)

    return render_to_response(
        'livesettings/text.txt', {'text': result}, mimetype='text/plain'
    )


def dump_yaml(settings):
    grouped_settings = {}
    for setting in settings:
        grouped_settings.setdefault(setting['group'], []).append(setting)

    buffer = StringIO.StringIO()

    for group in sorted(grouped_settings.keys()):
        buffer.write('# %s\n' % group)

        objects = {s['key']: s['value'] for s in grouped_settings[group]}

        objects = _create_language_hierarchy(objects)

        buffer.write(yaml.dump(objects, default_flow_style=False,
                               Dumper=yaml.SafeDumper))

        buffer.write('\n')

    output = buffer.getvalue().rstrip()
    buffer.close()

    return output


def _create_language_hierarchy(objects):
    # TODO: This is askbot specific so should be outside of livesettings
    tree = {}

    language_codes = [l[0].upper() for l in django_settings.LANGUAGES]

    for (name, value) in objects.iteritems():
        name_pieces = name.rsplit('_', 1)
        if len(name_pieces) == 2 and name_pieces[1] in language_codes:
            tree.setdefault(name_pieces[0], {})
            tree[name_pieces[0]][name_pieces[1].lower()] = value
        else:
            tree[name] = value

    return tree

export_as_python = never_cache(staff_member_required(export_as_python))
export_as_yaml = never_cache(staff_member_required(export_as_yaml))
