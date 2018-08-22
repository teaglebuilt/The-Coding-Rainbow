from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.utils.text import slugify
from memberships.models import UserMembership
import datetime

# Create your models here.
class Post(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length= 50)
    description = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/%Y/%m/$D/', null=True, blank=True)


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={ "slug": self.slug })

    def get_update_url(self):
        return reverse('blog:update', kwargs={ "slug": self.slug })

    def get_delete_url(self):
        return reverse('blog:delete', kwargs={ "slug": self.slug })

    class Meta:
            db_table = 'Post'


def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Post.objects.filter(slug=slug)
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" %(slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def pre_save_post_reciever(sender, instance, *args, **kwargs):
    slug = slugify(instance.title)
    exists = Post.objects.filter(slug=slug).exists()
    if exists:
        slug = "%s-%s" %(slug, instance.id)
    instance.slug = slug

pre_save.connect(pre_save_post_reciever, sender=Post)


class Author(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    membership = models.ForeignKey(UserMembership, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Author'
