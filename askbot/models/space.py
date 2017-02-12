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
    image = models.ImageField(upload_to='spaces')
    order_number = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (
            ('slug', 'language_code'),
            ('slug', 'order_number')
        )
        app_label = 'askbot'

    def save(self):
        # Auto-populate slug
        self.slug = slugify(self.name)
        # TODO: validate slug so that it does not clash with
        # existing urls
        super(Space, self).save()

    def get_absolute_url(self):
        return reverse('questions', kwargs={'space': self.slug})
