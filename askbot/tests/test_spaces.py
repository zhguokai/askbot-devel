from django.test import TestCase
from askbot import models
from askbot.search.state_manager import SearchState

class SpaceRedirectTests(TestCase):
    def test_redirect_added_on_space_rename(self):
        space = models.Space(description='blahblah',
                    name='Blah', language_code='en',
                    order_number=2)
        space.save()
        space = models.Space.objects.get(slug='blah')
        space.name = 'Putin'
        space.language_code = 'ru'
        space.save()
        redirects = models.SpaceRedirect.objects.filter(slug='blah')
        self.assertEqual(redirects.count(), 1)
        # Putin exists
        self.assertEqual(redirects[0].space.name, 'Putin')

        response = self.client.get('/blah/')
        ss = SearchState(space='putin')
        self.assertRedirects(response, ss.full_url())

