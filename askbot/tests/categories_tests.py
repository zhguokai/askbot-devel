from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import simplejson

from categories.models import Category

from askbot.conf import settings as askbot_settings
from askbot.views.cats import generate_tree


class TreeTests(TestCase):
    def setUp(self):
        root = Category.objects.create(name='Root')
        n1 = Category.objects.create(name='N1', parent=root)
        Category.objects.create(name='N2', parent=root)
        Category.objects.create(name='Child1', parent=n1)
        Category.objects.create(name='Child2', parent=n1)

    def test_python_tree(self):
        """
        Test that django-mptt builds the tree correctly. version 0.4.2 has a
        bug when populating the tree, it incorrectly grafts the Child1 and
        Child2 nodes under N2.
        """
        self.assertEqual(
            {
                "name": u"Root",
                "id": (1, 1),
                "children": [
                    {
                        "name": u"N1",
                        "id": (1, 2),
                        "children": [
                            {
                                "name": u"Child1",
                                "id": (1, 3),
                                "children": []
                            },
                            {
                                "name": u"Child2",
                                "id": (1, 5),
                                "children": []
                            }
                        ]
                    },
                    {
                        "name": u"N2",
                        "id": (1, 8),
                        "children": []
                    }

                ]
            },
            generate_tree()
        )


class EmptyTreeTests(TestCase):
    def test_python_tree(self):
        """Data structure generation shouldn't explode when tree is empty."""
        self.assertEqual({}, generate_tree())


class AjaxTests(TestCase):
    def ajax_get(self, path, data={}, follow=False, **extra):
        extra.update({'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        return self.client(path, data, follow, **extra)

    def ajax_post(self, path, data={}, content_type='application/x-www-form-urlencoded', follow=False,
            **extra):
        extra.update({'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        return self.client.post(path, data, content_type, follow, **extra)

    def ajax_post_json(self, path, data):
        return self.ajax_post(path, simplejson.dumps(data))


class ViewsTests(AjaxTests):
    def setUp(self):
        # An administrator user
        owner = User.objects.create_user(username='owner', email='owner@example.com', password='secret')
        owner.is_staff = True
        owner.is_superuser = True
        owner.save()
        # A normal user
        User.objects.create_user(username='user1', email='user1@example.com', password='123')
        # Setup a small category tree
        root = Category.objects.create(name='Root')
        self.c1 = Category.objects.create(name='Child1', parent=root)
        askbot_settings.update('ENABLE_CATEGORIES', True)

    def test_categories_off(self):
        """AJAX add category view shouldn't exist when master switch is off."""
        askbot_settings.update('ENABLE_CATEGORIES', False)
        r = self.ajax_post_json('/add_category/', {'name': 'Entertainment', 'parent': (1, 1)})
        self.assertEqual(r.status_code, 404)

    def test_add_category_no_permission(self):
        """Only administrator users should be able to add a category via the view."""
        self.client.login(username='user1', password='123')
        r = self.ajax_post_json('/add_category/', {'name': 'Health', 'parent': (1, 1)})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/json')
        self.assertContains(r, 'Sorry, but you cannot access this view')

    def test_add_category_exists(self):
        """Two categories with the same name shouldn't be allowed."""
        self.client.login(username='owner', password='secret')
        r = self.ajax_post_json('/add_category/', {'name': 'Child1', 'parent': (1, 1)})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/json')
        self.assertContains(r, 'There is already a category with that name')

    def add_category_success(self, post_data):
        """Helper method"""
        category_objects = Category.objects.count()
        r = self.ajax_post_json('/add_category/', post_data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/json')
        try:
            data = simplejson.loads(r.content)
        except Exception, e:
            self.Fail(str(e))
        self.assertTrue(data['success'])
        self.assertEqual(category_objects + 1, Category.objects.count())

    def test_add_category_success(self):
        """Valid new categories should be added to the database."""
        self.client.login(username='owner', password='secret')
        # A child of the root node
        self.add_category_success({'name': 'Child2', 'parent': (1, 1)})
        # A child of a non-root node
        self.add_category_success({'name': 'Child1', 'parent': (self.c1.tree_id, self.c1.lft)})

    def test_add_new_tree(self):
        """Test insertion of a new root-of-tree node."""
        self.client.login(username='owner', password='secret')
        category_objects = Category.objects.count()
        r = self.ajax_post_json('/add_category/', {'name': 'AnotherRoot', 'parent': None})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/json')
        try:
            data = simplejson.loads(r.content)
        except Exception, e:
            self.Fail(str(e))
        self.assertTrue(data['success'])
        self.assertEqual(category_objects + 1, Category.objects.count())
        self.assertEqual(Category.tree.root_nodes().filter(name='AnotherRoot').count(), 1)

    def test_add_invalid_parent(self):
        """Attempted insertion of a new category with an invalid parent should fail."""
        self.client.login(username='owner', password='secret')
        r = self.ajax_post_json('/add_category/', {'name': 'Foo', 'parent': (100, 20)})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/json')
        self.assertContains(r, "Requested parent node doesn't exist")
