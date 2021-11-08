import unittest

from pyramid import testing


class TutorialViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_hello_world(self):
        from codechallenge.app import good_evening

        request = testing.DummyRequest()
        response = good_evening(request)
        self.assertEqual(response.status_code, 200)


class TutorialFunctionalTests(unittest.TestCase):
    def setUp(self):
        from codechallenge import main
        app = main({})
        from webtest import TestApp

        self.testapp = TestApp(app)

    def test_hello_world(self):
        res = self.testapp.get('/', status=200)
        self.assertIn(b'<h1>Good Evening y\'all !!! Does it work? It does :)</h1>', res.body)
