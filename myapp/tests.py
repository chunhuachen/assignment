import json
import sqlalchemy, sqlalchemy.orm
from django.test import TestCase
from django.conf import settings
from sqlalchemy import create_engine
from myapp.models import Users, Base


# Create your tests here.
engine = create_engine(settings.DATABASE_ENGINE)
Base.metadata.create_all(engine)

class MyappTests(TestCase):

    def setUp(self):
        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        session = Session()
        session.query(Users).delete()
        session.commit()

    def test_create_update_delete_user(self):
        # normal create user1
        payload = {"account":"user1","pwd":"1234", "fullname":"user1 fullname"}
        resp = self.client.put('/myapp/create-user', payload, content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        result = json.loads(resp.content)
        self.assertTrue("token" in result)
        token_user1 = result["token"]

        # duplicate
        resp = self.client.put('/myapp/create-user', payload, content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        # no account
        payload = {"pwd":"1234", "fullname":"user1 fullname"}
        resp = self.client.put('/myapp/create-user', payload, content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        # no password
        payload = {"account":"user1","fullname":"user1 fullname"}
        resp = self.client.put('/myapp/create-user', payload, content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        # no fullname, allow
        payload = {"account":"user2","pwd":"1234"}
        resp = self.client.put('/myapp/create-user', payload, content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        result = json.loads(resp.content)
        token_user2 = result["token"]

        # normal update user1
        payload = {"account":"user1","fullname":"user1 new fullname"}
        resp = self.client.put('/myapp/update-user', payload, HTTP_AUTHORIZATION="Bearer "+token_user1, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        # update user1 with user2 token
        payload = {"account":"user1","fullname":"user1 new fullname"}
        resp = self.client.put('/myapp/update-user', payload, HTTP_AUTHORIZATION="Bearer "+token_user2, content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        # user1 detail
        resp = self.client.get('/myapp/detail/user1', HTTP_AUTHORIZATION="Bearer "+token_user1)
        self.assertEqual(resp.status_code, 200)
        result = json.loads(resp.content)
        self.assertTrue("user_detail" in result)
        self.assertEqual(result["user_detail"]["fullname"], "user1 new fullname")

        # delete user1 with user2 token
        resp = self.client.delete('/myapp/delete-user/user1', HTTP_AUTHORIZATION="Bearer "+token_user2, content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        # delete user1 without token
        resp = self.client.delete('/myapp/delete-user/user1', content_type='application/json')
        self.assertEqual(resp.status_code, 403)

        # normal delete user1
        resp = self.client.delete('/myapp/delete-user/user1', HTTP_AUTHORIZATION="Bearer "+token_user1, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

    def test_login_user(self):
        # create user1
        payload = {"account":"user1","pwd":"1234", "fullname":"user1 fullname"}
        resp = self.client.put('/myapp/create-user', payload, content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        result = json.loads(resp.content)
        token = result["token"]

        # normal user login
        payload = {"account":"user1","pwd":"1234"}
        resp = self.client.post('/myapp/login-user', payload, HTTP_AUTHORIZATION="Bearer "+token, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        result = json.loads(resp.content)
        self.assertTrue("token" in result)

        # wrong password
        payload = {"account":"user1","pwd":"1111"}
        resp = self.client.post('/myapp/login-user', payload, HTTP_AUTHORIZATION="Bearer "+token, content_type='application/json')
        self.assertEqual(resp.status_code, 401)

        # no such user
        payload = {"account":"user1234","pwd":"1111"}
        resp = self.client.post('/myapp/login-user', payload, HTTP_AUTHORIZATION="Bearer "+token, content_type='application/json')
        self.assertEqual(resp.status_code, 401)


    def test_get_user_info(self):
        # create user1
        payload = {"account":"user1","pwd":"1234", "fullname":"user1 fullname"}
        resp = self.client.put('/myapp/create-user', payload, content_type='application/json')
        result = json.loads(resp.content)
        token_user1 = result["token"]

        # create user2
        payload = {"account":"user2","pwd":"1234", "fullname":"user2 fullname"}
        resp = self.client.put('/myapp/create-user', payload, content_type='application/json')
        result = json.loads(resp.content)
        token_user2 = result["token"]

        # create user3 with the same fullname as user1
        payload = {"account":"user3","pwd":"1234", "fullname":"user1 fullname"}
        resp = self.client.put('/myapp/create-user', payload, content_type='application/json')
        result = json.loads(resp.content)
        token_user3 = result["token"]

        # user1 detail
        resp = self.client.get('/myapp/detail/user1', HTTP_AUTHORIZATION="Bearer "+token_user1)
        self.assertEqual(resp.status_code, 200)

        # list user1 detail with user2 token, should fail
        resp = self.client.get('/myapp/detail/user1', HTTP_AUTHORIZATION="Bearer "+token_user2)
        self.assertEqual(resp.status_code, 400)

        # list all users, should have 3 users
        resp = self.client.get('/myapp/list-all-users', HTTP_AUTHORIZATION="Bearer "+token_user2)
        self.assertEqual(resp.status_code, 200)
        result = json.loads(resp.content)
        self.assertTrue("users" in result)
        self.assertEqual(len(result["users"]), 3)

        # search user by full name
        payload = {"fullname":"no such full name"}
        resp = self.client.post('/myapp/search-user', payload, HTTP_AUTHORIZATION="Bearer "+token_user1, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        result = json.loads(resp.content)
        self.assertTrue("users" in result)
        self.assertEqual(len(result["users"]), 0)

        # search user by "user1 fullname", should have 2 (user1 and user3)
        payload = {"fullname":"user1 fullname"}
        resp = self.client.post('/myapp/search-user', payload, HTTP_AUTHORIZATION="Bearer "+token_user1, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        result = json.loads(resp.content)
        self.assertTrue("users" in result)
        self.assertEqual(len(result["users"]), 2)

        # search user by "user2 fullname", should have 1 only
        payload = {"fullname":"user2 fullname"}
        resp = self.client.post('/myapp/search-user', payload, HTTP_AUTHORIZATION="Bearer "+token_user1, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        result = json.loads(resp.content)
        self.assertTrue("users" in result)
        self.assertEqual(len(result["users"]), 1)




