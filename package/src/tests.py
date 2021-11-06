import unittest

from pyramid import testing


class TutorialViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_hello_world(self):
        from server.app import hello_world

        request = testing.DummyRequest()
        response = hello_world(request)
        self.assertEqual(response.status_code, 200)


class TutorialFunctionalTests(unittest.TestCase):
    def setUp(self):
        from server.app import get_app
        app = get_app()
        from webtest import TestApp

        self.testapp = TestApp(app)

    def test_hello_world(self):
        res = self.testapp.get('/', status=200)
        self.assertIn(b'<h1>Hello World!!!</h1>', res.body)
