import json
import bcrypt
import jwt
import datetime

from django.views     import View
from django.http      import JsonResponse
from my_settings      import SECRET, ALGORITHM

from .models          import User, Follow
from .utils           import login_decorator
from django.db.models import Q


class SignUpView(View):
    def post(self, request):
        data = json.loads(request.body)

        MINIMUM_PASSWORD_LENGTH = 8   
        
        try:
            if User.objects.filter(email=data['email']).exists(): 
                return JsonResponse({'message': 'ALREADY EXIST'}, status = 400)
            
            if '@' not in data['email'] or '.' not in data['email']:
                return JsonResponse({'message':'WRONG FORM'}, status = 400)

            if len(data['password']) < MINIMUM_PASSWORD_LENGTH:
                return JsonResponse({'message': 'TOO SHORT'}, status=400)

            hashed_password = bcrypt.hashpw(
                data['password'].encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')  
            
            User.objects.create(email = data['email'], password = hashed_password)

            return JsonResponse({'message': 'SUCCESS'}, status=200)
        
        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400) 
        
class SignInView(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            if not User.objects.filter(email=data['email']).exists(): 
                return JsonResponse({'message':'INVALID_USER'}, status=401)

            new_password = data['password'] 
            user         = User.objects.get(email = data['email'])  
            password     = user.password 

            if not bcrypt.checkpw(new_password.encode('utf-8'), password.encode('utf-8')):
                return JsonResponse({'message':'WRONG_PASSWORD'}, status=401)

            expire = datetime.datetime.utcnow() + datetime.timedelta(seconds=3600) 
          
            access_token = jwt.encode({'user_id': user.id, 'exp': expire}, SECRET['secret'], algorithm=ALGORITHM).decode('utf-8') 
            
            return JsonResponse({'Authorization': access_token}, status=200)

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)  

class FollowView(View):
    @login_decorator
    def post(self, request):
        try:
            data = json.loads(request.body)
            if not User.objects.filter(id=data['to_user_id']).exists():
                return JsonResponse({'message':'NOT FOUND'}, status=404)
            
            if data['follow_button'] == '+':
                Follow.objects.create(from_user=request.user, to_user_id=data['to_user_id'])
            elif data['follow_button'] == '-':
                Follow.objects.filter(Q(from_user=request.user) & Q(to_user_id=data['to_user_id'])).delete()
            
            return JsonResponse({'message':'SUCCESS'}, status=200)
        
        except KeyError:
            return JsonResponse({'message':'KEY ERROR'}, status=400)

    def get(self, request):
        user_id = request.GET.get('user-id', None)
        try:
            
            from_users = User.objects.get(id=user_id).follow_from_user.all()
            to_users   = User.objects.get(id=user_id).follow_to_user.all()

            results = [{
                'following': [user.to_user.id for user in from_users],
                'follower' : [user.from_user.id for user in to_users]
            }]
            return JsonResponse({'follow_list':results}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'message':'NOT FOUND'}, status=404)

