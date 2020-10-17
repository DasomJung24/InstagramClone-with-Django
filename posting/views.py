import json
import datetime

from django.views     import View
from django.http      import JsonResponse
from django.db.models import Q

from user.utils       import login_decorator
from user.models      import User
from .models          import Posting, Image, Comment, Like, CommentOfComment


class PostingDetailView(View):
    @login_decorator
    def post(self, request):
        data = json.loads(request.body)
        try:
            posting = Posting.objects.create(user=request.user, content=data.get('content', None))
            
            for image in data['image']:
                Image.objects.create(image=image, posting=posting)

            return JsonResponse({'message':'SUCCESS'}, status=200)
        
        except KeyError:
            return JsonResponse({'message':'KEY ERROR'}, status=400)

    def get(self, request, posting_id):
            try:
                posting = Posting.objects.get(id=posting_id)

                result = {
                    'id'        : posting_id,
                    'content'   : posting.content,
                    'image'     : [data.image for data in Image.objects.filter(posting=posting)],
                    'created_at': posting.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }

                return JsonResponse({'posting_data':[result]}, status=200)
            except Posting.DoesNotExist:
                return JsonResponse({'message':'NOT FOUND'}, status=404)

    @login_decorator
    def patch(self, request, posting_id):
        try:
            data = json.loads(request.body)
            posting = Posting.objects.get(id=posting_id)
            posting.content = data['content']
            posting.save()
            
            Image.objects.filter(posting_id=posting_id).delete()
            image_list = data['image']
            # for image in image_list:
            #     Image.objects.create(image=image, posting_id=posting_id)
            bulk_create_list = []
            for image in image_list:
                bulk_create_list.append(Image(image=image, posting_id=posting_id))
            Image.objects.bulk_create(bulk_create_list)
            

            # Image.objects.bulk_create([Image(image=image, posting_id=posting_id),])

            return JsonResponse({'message':'SUCCESS'}, status=200)
        
        except Posting.DoesNotExist:
            return JsonResponse({'message':'NOT FOUND'}, status=404)

    @login_decorator
    def delete(self, request, posting_id):
        try:
            Posting.objects.get(id=posting_id).delete()
            
            return JsonResponse({'message':'SUCCESS'}, status=200)
        
        except Posting.DoesNotExist:
            return JsonResponse({'message':'NOT FOUND'}, status=404)

class PostingListView(View):
    def get(self, request, user_id):
        posting = Posting.objects.filter(user_id=user_id).prefetch_related('image_set')

        results = [{
            'id'        : data.id,
            'content'   : data.content,
            'image'     : [data.image for data in Image.objects.filter(posting=data)],
            'created_at': data.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for data in posting]

        return JsonResponse({'posting_list':results}, status=200)

class CommentView(View):
    @login_decorator
    def post(self, request):
        data = json.loads(request.body)
        try:
            if not Posting.objects.filter(id=data['posting_id']).exists():
                return JsonResponse({'message':'NOT FOUND'}, status=404)

            Comment.objects.create(
                posting_id = data['posting_id'],
                user       = request.user,
                content    = data['content']
            )
            
            return JsonResponse({'message':'SUCCESS'}, status=200)
        
        except KeyError:
            return JsonResponse({'message':'KEY ERROR'}, status=400)

    def get(self, request):
            posting_id = request.GET.get('posting-id', None)
            if not Posting.objects.filter(id=posting_id).exists():
                return JsonResponse({'message':'NOT FOUND'}, status=404)
            
            results = Comment.objects.filter(posting_id=posting_id).select_related('user')
            result = [{
                'id'         : data.id,
                'content'    : data.content,
                'user_id'    : data.user.id,
                'posting_id' : posting_id,
                'created_at' : data.created_at.strftime('%Y-%m-%d %H:%M')
            } for data in results]
            
            return JsonResponse({'comment_data':result}, status=200)

    @login_decorator
    def delete(self, request, comment_id):
        try:
            Comment.objects.get(id=comment_id).delete()
            
            return JsonResponse({'message':'SUCCESS'}, status=200)
        
        except Comment.DoesNotExist:
            return JsonResponse({'message':'NOT FOUND'}, status=404)

class CommentOfCommentView(View):
    @login_decorator
    def post(self, request):
        data = json.loads(request.body)
        
        if not Comment.objects.filter(id=data['comment_id']).exists():
            return JsonResponse({'message':'NOT FOUND'}, status=404)
        
        CommentOfComment.objects.create(
            user          = request.user, 
            comment_id    = data['comment_id'],
            content       = data['content']
            )
        
        return JsonResponse({'message':'SUCCESS'}, status=200)
    
    def get(self, request):
        comment_id = request.GET.get('comment-id', None)
        if not Comment.objects.filter(id=comment_id).exists():
            return JsonResponse({'message':'NOT FOUND'}, status=404)

        comments = CommentOfComment.objects.filter(comment_id=comment_id).select_related('user')
        results = [{
            'id'        : data.id,
            'user_id'   : data.user.id,
            'content'   : data.content,
            'comment_id': data.comment.id
        } for data in comments]

        return JsonResponse({'comment_of_comment_list':results}, status=200)

class LikeView(View):
    @login_decorator
    def post(self, request, posting_id):
        data = json.loads(request.body)
        
        if not Posting.objects.filter(id=posting_id).exists():
            return JsonResponse({'message':'NOT FOUND'}, status=404)
        
        if Like.objects.filter(Q(user=request.user) & Q(posting_id=posting_id)).exists():
            Like.objects.filter(Q(user=request.user) & Q(posting_id=posting_id)).delete()  # 이미 좋아요를 누른 user라서 한번 더 누르면 좋아요 취소로 설정
        
        Like.objects.create(user=request.user, posting_id=posting_id)
        
        return JsonResponse({'message':'SUCCESS'}, status=200)

    def get(self, request, posting_id):
        if not Like.objects.filter(posting_id=posting_id).exists():
            return JsonResponse({'message':'NOT FOUND'}, status=404)
        
        likes = Like.objects.filter(posting_id=posting_id)
        results = [{
            'id'         : data.id,
            'posting_id' : posting_id,
            'user_id'    : data.user.id
        } for data in likes]
        
        return JsonResponse({'like_list':results}, status=200)