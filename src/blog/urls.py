from django.urls import path
from django.conf.urls import url
from .views import posts_list, posts_detail, create_post


app_name = 'blog'


urlpatterns = [
    url(r'^$', posts_list),
    url(r'^(?P<id>\d+)/$', posts_detail, name='details'),
    url(r'^create/$', create_post),

]