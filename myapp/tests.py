import json
from django.test import TestCase

# Create your tests here.

class MyappTests(TestCase):
    def setUp(self):
        pass

    def test_list_users(self):
        response = self.client.get('/myapp/list_user')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result, '')

