import json
import datetime
import jwt
import bcrypt

from django.test import TestCase, Client
from my_settings import SECRET, ALGORITHM

from user.utils  import login_decorator
from .models     import Posting, Image, Comment, CommentOfComment, Like
from user.models import User


class PostingTest(TestCase):
    def setUp(self):
        User.objects.create(
            id      =1,
            email   ='test@tes.tes',
            password=bcrypt.hashpw('123456789'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        Posting.objects.create(
            id     =1,
            user_id=1,
            content='hihi'
        )
        Posting.objects.create(
            id     =2,
            user_id=1,
            content='bye'
        )
        Image.objects.create(
            id        =1,
            image     ='cat.cat',
            posting_id=1
        )
        Image.objects.create(
            id        =2,
            image     ='cat1.cat',
            posting_id=1
        )
        Image.objects.create(
            id        =3,
            image     ='dog.dog',
            posting_id=2
        )
        expire     = datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)  
        self.token = jwt.encode({'user_id': 1, 'exp': expire}, SECRET['secret'], algorithm=ALGORITHM).decode('utf-8') 

    def tearDown(self):
        User.objects.all().delete()
        Posting.objects.all().delete()
        Image.objects.all().delete()

    def test_post_posting_success(self):
        client = Client()

        headers = {'HTTP_Authorization':self.token}
        data = {
            'content': 'hi',
            'image'  : 'hi.hi'
        }
        response = client.post('/posting', json.dumps(data), **headers, content_type='application/json')
        self.assertEqual(response.json(), {'message': 'SUCCESS'})
        self.assertEqual(response.status_code, 200)

    def test_posting_key_error(self):
        client = Client()

        headers = {'HTTP_Authorization': self.token}
        data = {
            'content': 'hi',
            'imag'   : 'hi.hi'
        }
        response = client.post('/posting', json.dumps(data), **headers, content_type='application/json')
        self.assertEqual(response.json(), {'message': 'KEY ERROR'})
        self.assertEqual(response.status_code, 400)

    def test_posting_get_success(self):
        client = Client()
        User.objects.create(
            id      =10,
            email   ='test@tes.test',
            password=bcrypt.hashpw('123456789'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        posting = Posting.objects.create(
            id     =7,
            user_id=10,
            content='hihi'
        )
        Image.objects.create(
            id        =5,
            image     ='cat.cat',
            posting_id=7
        )
        Image.objects.create(
            id        =9,
            image     ='cat1.cat',
            posting_id=7
        )
        response = client.get('/posting/7')
        self.assertEqual(response.json(), 
            {'posting_data':[{
                'id'        : 7,
                'content'   : 'hihi',
                'image'     : ['cat.cat', 'cat1.cat'],
                'created_at': posting.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }]}
        )
        self.assertEqual(response.status_code, 200)

    def test_get_posting_not_exist(self):
        client = Client()

        response = client.get('/posting/10')
        self.assertEqual(response.json(), {'message': 'NOT FOUND'})
        self.assertEqual(response.status_code, 404)

    def test_patch_posting_success(self):
        client = Client()

        headers = {'HTTP_Authorization': self.token}

        data = {
            'content': 'happy~',
            'image'  : ['happy.happy', 'hihihi.hihi']
        }
        response = client.patch('/posting/2', json.dumps(data), **headers, content_type='application/json')
        self.assertEqual(response.json(), {'message': 'SUCCESS'})
        self.assertEqual(response.status_code, 200)

    def test_patch_posting_not_exist(self):
        client = Client()
        
        headers = {'HTTP_Authorization': self.token}

        data = {
            'content': 'happy~',
            'image'  : ['happy.happy', 'hihihi.hihi']
        }
        response = client.patch('/posting/30', json.dumps(data), **headers, content_type='application/json')
        self.assertEqual(response.json(), {'message': 'NOT FOUND'})
        self.assertEqual(response.status_code, 404)

    def test_posting_delete_success(self):
        client = Client()

        headers = {'HTTP_Authorization': self.token}

        response = client.delete('/posting/1', **headers)
        self.assertEqual(response.json(), {'message': 'SUCCESS'})
        self.assertEqual(response.status_code, 200)

    def test_delete_posting_not_exist(self):
        client = Client()

        headers = {'HTTP_Authorization': self.token}

        response = client.delete('/posting/20', **headers)
        self.assertEqual(response.json(), {'message': 'NOT FOUND'})
        self.assertEqual(response.status_code, 404)


class PostingListTest(TestCase):
    def setUp(self):
        User.objects.create(
            id      =1,
            email   ='test@tes.tes',
            password=bcrypt.hashpw('123456789'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        Posting.objects.create(
            id     =1,
            user_id=1,
            content='hihi'
        )
        Image.objects.create(
            id        =1,
            image     ='cat.cat',
            posting_id=1
        )
        Image.objects.create(
            id        =2,
            image     ='cat1.cat',
            posting_id=1
        )

    def tearDown(self):
        User.objects.all().delete()
        Posting.objects.all().delete()
        Image.objects.all().delete()

    def test_get_posting_list_success(self):
        client = Client()
        User.objects.create(
            id      =11,
            email   ='test@tes.tes',
            password=bcrypt.hashpw('123456789'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        posting = Posting.objects.create(
            id     =11,
            user_id=11,
            content='hihi'
        )
        Image.objects.create(
            id        =11,
            image     ='cat.cat',
            posting_id=11
        )
        Image.objects.create(
            id        =21,
            image     ='cat1.cat',
            posting_id=11
        )
        response = client.get('/posting/list/11')
        self.assertEqual(response.json(), 
            {'posting_list': [{
                'id'        : 11,
                'content'   : 'hihi',
                'image'     : ['cat.cat', 'cat1.cat'],
                'created_at': posting.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }]}
        )
        self.assertEqual(response.status_code, 200)


class CommentTest(TestCase):
    maxDiff = None
    def setUp(self):
        User.objects.create(
            id      =1,
            email   ='test@tes.tes',
            password=bcrypt.hashpw('123456789'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        Posting.objects.create(
            id     =1,
            user_id=1,
            content='hihi'
        )
        Image.objects.create(
            id        =1,
            posting_id=1,
            image     ='gi.gi'
        )
        Comment.objects.create(
            id        =1,
            user_id   =1,
            posting_id=1,
            content   ='aaaaa'
        )
        expire     = datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)  
        self.token = jwt.encode({'user_id': 1, 'exp': expire}, SECRET['secret'], algorithm=ALGORITHM).decode('utf-8') 

    def tearDown(self):
        User.objects.all().delete()
        Posting.objects.all().delete()
        Comment.objects.all().delete()

    def test_post_comment_success(self):
        client  = Client()
        headers = {'HTTP_Authorization': self.token}
        
        data = {
            'posting_id': 1,
            'content'   : 'lol'
        }
        response = client.post('/posting/comment', json.dumps(data), **headers, content_type='application/json')
        self.assertEqual(response.json(), {'message': 'SUCCESS'})
        self.assertEqual(response.status_code, 200)

    def test_post_comment_posting_not_exist(self):
        client  = Client()
        headers = {'HTTP_Authorization': self.token}
        
        data = {
            'posting_id': 3,
            'content'   : 'ddd'
        }
        response = client.post('/posting/comment', json.dumps(data), **headers, content_type='application/json')
        self.assertEqual(response.json(), {'message': 'NOT FOUND'})
        self.assertEqual(response.status_code, 404)

    def test_post_comment_key_error(self):
        client  = Client()
        headers = {'HTTP_Authorization':self.token}
       
        data = {
            'postingid': 1,
            'content'  : 'ddd'
        }
        response = client.post('/posting/comment', json.dumps(data), **headers, content_type='application/json')
        self.assertEqual(response.json(), {'message': 'KEY ERROR'})
        self.assertEqual(response.status_code, 400)

    def test_get_all_comment_success(self):
        client = Client()

        User.objects.create(
            id      =11,
            email   ='test@tes.tes',
            password=bcrypt.hashpw('123456789'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        Posting.objects.create(
            id     =11,
            user_id=11,
            content='hihi'
        )
        Image.objects.create(
            id        =12,
            posting_id=11,
            image     ='gi.gi'
        )
        comment = Comment.objects.create(
            id        =10,
            user_id   =11,
            posting_id=11,
            content   ='aaaaa'
        )
        response = client.get('/posting/comment?posting-id=1')
        self.assertEqual(response.json(), 
            {
                'comment_data': [{
                    'id'        : 1,
                    'content'   : 'aaaaa',
                    'user_id'   : 1,
                    'posting_id': '1',
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
                }]
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_get_comment_posting_not_exist(self):
        client = Client()

        response = client.get('/posting/comment?posting-id=19')
        self.assertEqual(response.json(), {'message': 'NOT FOUND'})
        self.assertEqual(response.status_code, 404)

    def test_delete_comment_success(self):
        client = Client()

        headers = {'HTTP_Authorization': self.token}

        response = client.delete('/posting/comment/1', **headers)
        self.assertEqual(response.json(), {'message': 'SUCCESS'})
        self.assertEqual(response.status_code, 200)

    def test_delete_comment_not_exist(self):
        client = Client()

        headers = {'HTTP_Authorization': self.token}

        response = client.delete('/posting/comment/4', **headers)
        self.assertEqual(response.json(), {'message': 'NOT FOUND'})
        self.assertEqual(response.status_code, 404)


class CommentOfCommentTest(TestCase):
    def setUp(self):
        User.objects.create(
            id      =1,
            email   ='test@tes.tes',
            password=bcrypt.hashpw('123456789'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        Posting.objects.create(
            id     =1,
            user_id=1,
            content='hihi'
        )
        Image.objects.create(
            id        =1,
            posting_id=1,
            image     ='gi.gi'
        )
        Comment.objects.create(
            id        =1,
            user_id   =1,
            posting_id=1,
            content   ='aaaaa'
        )
        CommentOfComment.objects.create(
            id        =1,
            content   ='hihi',
            user_id   =1,
            comment_id=1
        )
        expire     = datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)  
        self.token = jwt.encode({'user_id': 1, 'exp': expire}, SECRET['secret'], algorithm=ALGORITHM).decode('utf-8') 
    
    def tearDown(self):
        User.objects.all().delete()
        Posting.objects.all().delete()
        Image.objects.all().delete()
        Comment.objects.all().delete()

    def test_commentofcomment_post_success(self):
        client = Client()

        headers = {'HTTP_Authorization': self.token}

        data = {
            'comment_id': 1,
            'content'   : 'bbbbb'
        }
        response = client.post('/posting/commentofcomment', json.dumps(data), **headers, content_type='application/json')
        self.assertEqual(response.json(), {'message': 'SUCCESS'})
        self.assertEqual(response.status_code, 200)

    def test_commentofcomment_post_comment_not_exist(self):
        client = Client()

        headers = {'HTTP_Authorization': self.token}

        data = {
            'comment_id': 5,
            'content'   : 'bbbbb'
        }
        response = client.post('/posting/commentofcomment', json.dumps(data), **headers, content_type='application/json')
        self.assertEqual(response.json(), {'message': 'NOT FOUND'})
        self.assertEqual(response.status_code, 404)

    def test_get_commentofcomment_success(self):
        client = Client()

        response = client.get('/posting/commentofcomment?comment-id=1')
        self.assertEqual(response.json(), 
            {
                'comment_of_comment_list':[{
                    'id'        : 1,
                    'user_id'   : 1,
                    'content'   : 'hihi',
                    'comment_id': 1
                }]
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_get_commentofcomment_comment_not_exist(self):
        client = Client()

        response = client.get('/posting/commentofcomment?comment-id=10')
        self.assertEqual(response.json(), {'message': 'NOT FOUND'})
        self.assertEqual(response.status_code, 404)


class LikeTest(TestCase):
    def setUp(self):
        User.objects.create(
            id      =1,
            email   ='test@tes.tes',
            password=bcrypt.hashpw('123456789'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        User.objects.create(
            id      =2,
            email   ='test@tes.test',
            password=bcrypt.hashpw('123456789'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        Posting.objects.create(
            id     =1,
            user_id=1,
            content='hihi1'
        )
        Posting.objects.create(
            id     =2,
            user_id=2,
            content='hihi2'
        )
        Posting.objects.create(
            id     =3,
            user_id=1,
            content='hihi3'
        )
        Image.objects.create(
            id        =1,
            posting_id=1,
            image     ='gi1.gi'
        )
        Image.objects.create(
            id        =2,
            posting_id=3,
            image     ='gi2.gi'
        )
        Image.objects.create(
            id        =3,
            posting_id=2,
            image     ='gi3.gi'
        )
        Like.objects.create(
            id        =1,
            user_id   =1,
            posting_id=3
        )
        Like.objects.create(
            id        =2,
            user_id   =2,
            posting_id=1
        )
        Like.objects.create(
            id        =3,
            user_id   =1,
            posting_id=2
        )
        expire     = datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)  
        self.token = jwt.encode({'user_id': 1, 'exp': expire}, SECRET['secret'], algorithm=ALGORITHM).decode('utf-8') 

    def tearDown(self):
        User.objects.all().delete()
        Posting.objects.all().delete()
        Like.objects.all().delete()

    def test_post_like_success(self):
        client = Client()

        headers = {'HTTP_Authorization': self.token}
        data = {}
        response = client.post('/posting/like/2', json.dumps(data), **headers, content_type='application/json')
        self.assertEqual(response.json(), {'message': 'SUCCESS'})
        self.assertEqual(response.status_code, 200)

    def test_post_like_posting_not_exist(self):
        client = Client()

        headers = {'HTTP_Authorization': self.token}
        data= {}
        response = client.post('/posting/like/10', json.dumps(data), **headers, content_type='application/json')
        self.assertEqual(response.json(), {'message': 'NOT FOUND'})
        self.assertEqual(response.status_code, 404)

    def test_get_like_success(self):
        client = Client()

        response = client.get('/posting/like/1')
        self.assertEqual(response.json(), 
            {
                'like_list': [{
                    'id'        : 2,
                    'posting_id': 1,
                    'user_id'   : 2
                }]
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_get_like_not_exist(self):
        client = Client()

        response = client.get('/posting/like/10')
        self.assertEqual(response.json(), {'message': 'NOT FOUND'})
        self.assertEqual(response.status_code, 404)
