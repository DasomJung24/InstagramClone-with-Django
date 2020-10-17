import json
import bcrypt
import jwt
import datetime

from django.test import TestCase, Client
from my_settings import SECRET, ALGORITHM

from .models     import User, Follow

class SignUpTest(TestCase):
    def setUp(self):
        User.objects.create(
            email    = 'test1@naver.com',
            password = bcrypt.hashpw('123456789'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))

    def tearDown(self):
        User.objects.all().delete()
    
    def test_sign_up_post_success(self):
        client = Client()

        user = {
            'email'    : 'test2@naver.com',
            'password' : '1234567890'
        }
        response = client.post('/user/signup', json.dumps(user), content_type='application/json')
        self.assertEqual(response.json(), {'message':'SUCCESS'})
        self.assertEqual(response.status_code, 200)

    def test_sign_up_email_exist(self):
        client = Client()

        user = {
            'email'    : 'test1@naver.com',
            'password' : '1234567890'
        }
        response = client.post('/user/signup', json.dumps(user), content_type='application/json')
        self.assertEqual(response.json(), {'message':'ALREADY EXIST'})
        self.assertEqual(response.status_code, 400)

    def test_sign_up_email_wrong_form(self):
        client = Client()

        user = {
            'email'    : 'test2naver.com',
            'password' : '1234567890'
        }
        response = client.post('/user/signup', json.dumps(user), content_type='application/json')
        self.assertEqual(response.json(), {'message':'WRONG FORM'})
        self.assertEqual(response.status_code, 400)

    def test_sign_up_password_shorter_than_minimum(self):
        client = Client()

        user = {
            'email'    : 'test3@naver.com',
            'password' : '123'
        }
        response = client.post('/user/signup', json.dumps(user), content_type='application/json')
        self.assertEqual(response.json(), {'message':'TOO SHORT'})
        self.assertEqual(response.status_code, 400)

    def test_sign_up_key_error(self):
        client = Client()

        user = {
            'emai'     : 'test3@naver.com',
            'password' : '1234567890'
        }
        response = client.post('/user/signup', json.dumps(user), content_type='application/json')
        self.assertEqual(response.json(), {'message':'KEY_ERROR'})
        self.assertEqual(response.status_code, 400)

class SignInTest(TestCase):
    def setUp(self):
        User.objects.create(
            email    = 'test1@naver.com',
            password = bcrypt.hashpw('1234567890'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')  
        )
        
    def tearDown(self):
        User.objects.all().delete()

    def test_sign_in_post_success(self):
        client = Client()

        user = {
            'email'    : 'test1@naver.com',
            'password' : '1234567890'
        }
        response = client.post('/user/signin', json.dumps(user), content_type='application/json')
        equal = [i for i in response.json().keys()]
        self.assertEqual(equal[0], 'Authorization')
        self.assertEqual(response.status_code, 200)

    def test_sign_in_user_not_exist(self):
        client = Client()

        user = {
            'email'    : 'test@naver.com',
            'password' : '123456789'
        }
        response = client.post('/user/signin', json.dumps(user), content_type='application/json')
        self.assertEqual(response.json(), {'message':'INVALID_USER'})
        self.assertEqual(response.status_code, 401)

    def test_sign_in_password_is_wrong(self):
        client = Client()

        user = {
            'email'    : 'test1@naver.com',
            'password' : '123456777'
        }
        response = client.post('/user/signin', json.dumps(user), content_type='application/json')
        self.assertEqual(response.json(), {'message':'WRONG_PASSWORD'})
        self.assertEqual(response.status_code, 401)

    def test_sign_in_key_error(self):
        client = Client()

        user = {
            'email'   : 'test1@naver.com',
            'pasword' : '123456789'
        }
        response = client.post('/user/signin', json.dumps(user), content_type='application/json')
        self.assertEqual(response.json(), {'message':'KEY_ERROR'})
        self.assertEqual(response.status_code, 400)

class FollowTest(TestCase):
    def setUp(self):
        User.objects.create(
            id       = 1,
            email    = 'test1@naver.com',
            password = bcrypt.hashpw('1234567890'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        User.objects.create(
            id       = 2,
            email    = 'test2@naver.com',
            password = bcrypt.hashpw('1234567890'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        User.objects.create(
            id       = 3,
            email    = 'test3@naver.com',
            password = bcrypt.hashpw('1234567890'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        User.objects.create(
            id       = 4,
            email    = 'test4@naver.com',
            password = bcrypt.hashpw('1234567890'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        User.objects.create(
            id       = 5,
            email    = 'test5@naver.com',
            password = bcrypt.hashpw('1234567890'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        User.objects.create(
            id       = 6,
            email    = 'test6@naver.com',
            password = bcrypt.hashpw('1234567890'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        Follow.objects.create(
            id           = 1,
            from_user_id = 1,
            to_user_id   = 3
        )
        Follow.objects.create(
            id           = 2,
            from_user_id = 2,
            to_user_id   = 1
        )
        Follow.objects.create(
            id           = 3,
            from_user_id = 4,
            to_user_id   = 1
        )
        Follow.objects.create(
            id           = 4,
            from_user_id = 5,
            to_user_id   = 1
        )
        expire = datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)  
        self.token = jwt.encode({'user_id': 1, 'exp': expire}, SECRET['secret'], algorithm=ALGORITHM).decode('utf-8') 

    def tearDown(self):
        User.objects.all().delete()
        Follow.objects.all().delete()

    def test_follow_to_user_success(self):
        client = Client()
        
        headers = {'HTTP_Authorization':self.token}
        data = {
            'to_user_id'    : 4,
            'follow_button' : '+'
        }
        response = client.post('/user/follow', json.dumps(data), **headers, content_type='application/json')
        self.assertEqual(response.json(), {'message':'SUCCESS'})
        self.assertEqual(response.status_code, 200)

    def test_follow_to_user_not_exist(self):
        client = Client()

        headers = {'HTTP_Authorization':self.token}
        data = {
            'to_user_id' : 10
        }
        response = client.post('/user/follow', json.dumps(data), **headers, content_type='application/json')
        self.assertEqual(response.json(), {'message':'NOT FOUND'})
        self.assertEqual(response.status_code, 404)

    def test_follow_key_error(self):
        client = Client()

        headers = {'HTTP_Authorization':self.token}
        data = {
            'user_id' : 4
        }
        response = client.post('/user/follow', json.dumps(data), **headers, content_type='application/json')
        self.assertEqual(response.json(), {'message':'KEY ERROR'})
        self.assertEqual(response.status_code, 400)

    def test_follow_get_all(self):
        client = Client()

        response = client.get('/user/follow?user-id=1')
        self.assertEqual(response.json(), 
            {
                'follow_list':[{
                    'following' : [3],
                    'follower'  : [2,4,5]
                }]}
        )
        self.assertEqual(response.status_code, 200)

    def test_follow_get_user_id_not_exist(self):
        client = Client()

        response = client.get('/user/follow?user-id=10')
        self.assertEqual(response.json(), {'message':'NOT FOUND'})
        self.assertEqual(response.status_code, 404)