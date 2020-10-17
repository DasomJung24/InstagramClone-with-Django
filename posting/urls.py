from django.urls import path
from .           import views

app_name = 'posting'
urlpatterns = [
    path('', views.PostingDetailView.as_view()),
    path('/<int:posting_id>', views.PostingDetailView.as_view()),
    path('/list/<int:user_id>', views.PostingListView.as_view()),
    path('/comment', views.CommentView.as_view()),
    path('/comment/<int:comment_id>', views.CommentView.as_view()),
    path('/commentofcomment', views.CommentOfCommentView.as_view()),
    path('/like/<int:posting_id>', views.LikeView.as_view()),
]