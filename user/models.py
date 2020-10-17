from django.db     import models

class User(models.Model):
    email            = models.CharField(max_length=50)
    password         = models.CharField(max_length=300)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)
    follower         = models.ManyToManyField('self', symmetrical=False, through='Follow')
    
    def __str__(self):
        return self.email

    class Meta:
        db_table = 'users'

class Follow(models.Model):
    from_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='follow_from_user'
    )
    to_user   = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='follow_to_user'
    )

    class Meta:
        db_table = 'follows'