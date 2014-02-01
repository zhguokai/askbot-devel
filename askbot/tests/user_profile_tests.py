from askbot.tests.utils import AskbotTestCase

class UserProfileTests(AskbotTestCase):
    def test_first_user_is_admin(self):
        u = self.create_user()
        self.assertEqual(u.is_superuser, True)
        self.assertEqual(u.is_staff, True)
