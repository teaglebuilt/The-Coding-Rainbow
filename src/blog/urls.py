from django.urls import path
from django.conf.urls import url
from .views import posts_list, post_detail, create_post, post_update, post_delete



app_name = 'blog'


urlpatterns = [
    url(r'^$', posts_list),
    url(r'^create/$', create_post),
    url(r'^(?P<slug>[\w-]+)/update/$', post_update, name='update'),
    url(r'^(?P<slug>[\w-]+)/delete/$', post_delete, name='delete'),
    url(r'^(?P<slug>[\w-]+)/$', post_detail, name='detail'),
]