from django.db   import models
from user.models import User


class Posting(models.Model):
    user       = models.ForeignKey('user.User', on_delete=models.CASCADE)
    content    = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

    class Meta:
        db_table = 'postings'


class Image(models.Model):
    image   = models.URLField()
    posting = models.ForeignKey(Posting, on_delete=models.CASCADE)

    def __str__(self):
        return self.posting.content

    class Meta:
        db_table = 'images'


class Comment(models.Model):
    posting    = models.ForeignKey(Posting, on_delete=models.CASCADE)
    user       = models.ForeignKey('user.User', on_delete=models.CASCADE)
    content    = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.posting.content
    
    class Meta:
        db_table = 'comments'


class Like(models.Model):
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    posting = models.ForeignKey(Posting, on_delete=models.CASCADE)

    def __str__(self):
        return self.posting.content

    class Meta:
        db_table = 'likes'


class CommentOfComment(models.Model):
    content    = models.CharField(max_length=500)
    user       = models.ForeignKey('user.User', on_delete=models.CASCADE)
    comment    = models.ForeignKey(Comment, on_delete=models.CASCADE)

    def __str__(self):
        return self.content 

    class Meta:
        db_table = 'comment_of_comment'