from django.conf import settings
from django.utils.translation import get_language

from haystack import indexes
from haystack.query import SearchQuerySet

from askbot.models import Post, Thread, User

class ThreadIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField()
    tags = indexes.MultiValueField()

    def get_model(self):
        return Thread

    def index_queryset(self, using=None):
        if getattr(settings, 'ASKBOT_MULTILINGUAL', True):
            lang_code = get_language()[:2]
            return self.get_model().objects.filter(language_code=lang_code,
                                                  posts__deleted=False)
        else:
            return self.get_model().objects.filter(posts__deleted=False)

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    post_text = indexes.CharField(model_attr='text')
    author = indexes.CharField()
    thread_id = indexes.IntegerField(model_attr='thread__pk')

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        if getattr(settings, 'ASKBOT_MULTILINGUAL', True):
            lang_code = get_language()[:2]
            return self.get_model().objects.filter(language_code=lang_code,
                                                  deleted=False)
        else:
            return self.get_model().objects.filter(deleted=False)

class UserIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return User

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

class AskbotSearchQuerySet(SearchQuerySet):

    def _determine_backend(self):
        '''This is a hack somehow connection_router got wrong values
        from setting and did not loaded the LanguageRouter'''

        from haystack import connections, connection_router
        # A backend has been manually selected. Use it instead.
        if self._using is not None:
            self.query = connections[self._using].get_query()
            return

        # No backend, so rely on the routers to figure out what's right.
        hints = {}

        if self.query:
            hints['models'] = self.query.models

        backend_alias = connection_router.for_read(**hints)

        if isinstance(backend_alias, (list, tuple)) and len(backend_alias):
            # We can only effectively read from one engine.
            backend_alias = backend_alias[0]

        # The ``SearchQuery`` might swap itself out for a different variant
        # here.
        if self.query:
            self.query = self.query.using(backend_alias)
        else:
            self.query = connections[backend_alias].get_query()

    def get_django_queryset(self, model_klass=Thread):
        '''dirty hack because models() method from the
        SearchQuerySet does not work </3'''
        id_list = []
        for r in self:
            if r.model_name in ['thread','post'] \
                    and model_klass._meta.object_name.lower() == 'thread':
                if getattr(r, 'thread_id'):
                    id_list.append(r.thread_id)
                else:
                    id_list.append(r.pk)
            elif r.model_name == model_klass._meta.object_name.lower():
                #FIXME: add a highlight here?
                id_list.append(r.pk)

        if model_klass == User:
            return model_klass.objects.filter(id__in=set(id_list))
        else:
            return model_klass.objects.filter(id__in=set(id_list))
