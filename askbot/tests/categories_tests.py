from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import simplejson

from categories.models import Category

from askbot.views.cats import generate_tree


class TreeTests(TestCase):
    def setUp(self):
        # TODO: Actually there is no need to build the tree using the mptt API.
        # The failure was in django-mptt, change this back to normal Django
        # model instatiations
        root = Category(name='Root')
        root.insert_at(target=None, save=True)
        n1 = Category(name='N1')
        n1.insert_at(target=root, position='last-child', save=True)
        Category(name='N2').insert_at(target=root, position='last-child', save=True)
        Category(name='Child1').insert_at(target=n1, position='last-child', save=True)
        Category(name='Child2').insert_at(target=n1, position='last-child', save=True)

    def test_python_tree(self):
        """
        Test that django-mptt build the tree correctly. version 0.4.2 hasa bug
        when populating the tree, it incorrectly grafts the Child1 and Child2
        nodes under N2.
        """
        self.assertEqual(
            {
                "name": "Root",
                "children": [
                    {
                        "name": "N1",
                        "children": [
                            {
                                "name": "Child1",
                                "children": []
                            },
                            {
                                "name": "Child2",
                                "children": []
                            }
                        ]
                    },
                    {
                        "name": "N2",
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


class ViewsTests(AjaxTests):
    def setUp(self):
        # A administrator user
        owner = User.objects.create_user(username='owner', email='owner@example.com', password='secret')
        owner.is_staff = True
        owner.is_superuser = True
        owner.save()
        # A normal user
        User.objects.create_user(username='user1', email='user1@example.com', password='123')
        # Setup a small category tree
        root = Category.objects.create(name='Root')
        Category.objects.create(name='Child1', parent=root)

    def test_add_category_no_permission(self):
        """Only administrator users should be able to add a category via the view."""
        self.client.login(username='user1', password='123')
        r = self.ajax_post('/add_category/', simplejson.dumps({'new_cat': 'Health', 'parent': 'Root'}))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/json')
        self.assertContains(r, 'Sorry, but you cannot access this view')

    def test_add_category_exists(self):
        """Two categories with the same name shouldn't be allowed."""
        self.client.login(username='owner', password='secret')
        r = self.ajax_post('/add_category/', simplejson.dumps({'new_cat': 'Child1', 'parent': 'Root'}))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/json')
        self.assertContains(r, 'There is already a category with that name')

    def test_add_category_success(self):
        """Valid new category should be added to the database."""
        self.client.login(username='owner', password='secret')
        category_objects = Category.objects.count()
        r = self.ajax_post('/add_category/', simplejson.dumps({'new_cat': 'Child2', 'parent': 'Root'}))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/json')
        try:
            data = simplejson.loads(r.content)
        except Exception, e:
            self.Fail(str(e))
        self.assertTrue(data['success'])
        self.assertEqual(category_objects + 1, Category.objects.count())
