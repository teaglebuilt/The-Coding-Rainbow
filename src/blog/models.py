from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from memberships.models import UserMembership
import datetime

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length= 50)
    description = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:details', kwargs={'id': self.id})

    class Meta:
            db_table = 'Post'



class Author(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    membership = models.ForeignKey(UserMembership, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Author'
