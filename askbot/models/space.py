from django.db import models
from django.core.urlresolvers import reverse
from askbot.models.fields import LanguageCodeField
from askbot.utils.slug import slugify

def get_space(slug):
    if not slug:
        return None
    try:
        return Space.objects.get(slug=slug)
    except Space.DoesNotExist:
        return None

def get_primary_space():
    try:
        return Space.objects.order_by('id')[0]
    except IndexError:
        return None
    

class Space(models.Model):
    description = models.TextField()
    name = models.CharField(max_length=128, unique=True)
    language_code = LanguageCodeField()
    slug = models.CharField(max_length=128, unique=True)
    image = models.ImageField(upload_to='spaces', null=True, blank=True)
    order_number = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (
            ('slug', 'language_code'),
            ('slug', 'order_number')
        )
        app_label = 'askbot'

    def __unicode__(self):
        return self.name

    @classmethod
    def from_db(cls, db, field_names, values):
        # default implementation of from_db() (could be replaced
        # with super())
        if cls._deferred:
            instance = cls(**zip(field_names, values))
        else:
            instance = cls(*values)
        instance._state.adding = False
        instance._state.db = db
        # customization to store the original field values on the instance
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def save(self):
        # Auto-populate slug
        self.slug = slugify(self.name)
        # TODO: validate slug so that it does not clash with
        # existing urls
        if not self._state.adding:
            old_slug = self._loaded_values['slug']
            if self.slug != old_slug:
                #create a redirect object
                redirect = SpaceRedirect()
                redirect.space = self
                redirect.slug = old_slug
                redirect.language_code = self.language_code
                redirect.save()

        super(Space, self).save()

    def get_absolute_url(self):
        return reverse('questions', kwargs={'space_name': self.slug})


class SpaceRedirect(models.Model):
    slug = models.CharField(max_length=128, unique=True)
    space = models.ForeignKey(Space, related_name='redirects')
    language_code = LanguageCodeField()

    class Meta:
        app_label = 'askbot'
