from django.test import TestCase
from askbot.tests.utils import AskbotTestCase
from askbot import models
from askbot.exceptions import SpaceNotEmptyError
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

class SpaceTests(AskbotTestCase):
    def test_delete_non_empty_space_raises_error(self):
        space = models.Space(description='blahblah',
                    name='Blah', language_code='en',
                    order_number=2)
        space.save()
        u = self.create_user()
        q = self.post_question(user=u, space=space)
        with self.assertRaises(SpaceNotEmptyError):
            space.delete()

    def test_delete_empty_space_works(self):
        space = models.Space(description='blahblah',
                    name='Blah', language_code='en',
                    order_number=2)
        space.save()
        try:
            space.delete()
        except SpaceNotEmptyError:
            self.fail('unexpected test fail')
