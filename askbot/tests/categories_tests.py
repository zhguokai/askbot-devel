from django.test import TestCase

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
