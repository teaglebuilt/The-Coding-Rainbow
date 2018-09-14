from django.urls import path
from django.conf.urls import url
from .views import (
    posts_list,
    post_detail,
    post_create,
    post_update,
    post_delete,
    PostLikeToggle,
    PostLikeAPIToggle,
    newsletter_signup,
    newsletter_unsubscribe,
    search_list_view,
)



app_name = 'blog'


urlpatterns = [
    url(r'^$', posts_list, name='blog'),
    url(r'^create/$', post_create),
    url(r'^(?P<slug>[\w-]+)/update/$', post_update, name='update'),
    url(r'^(?P<slug>[\w-]+)/delete/$', post_delete, name='delete'),
    url(r'^(?P<slug>[\w-]+)/$', post_detail, name='detail'),
    url(r'^(?P<slug>[\w-]+)/like/$', PostLikeToggle.as_view(), name='like'),
    url(r'^api/(?P<slug>[\w-]+)/like/$', PostLikeAPIToggle.as_view(), name='like_api'),
    url(r'sign_up/$', newsletter_signup, name='newsletter_signup'),
    url(r'unsubscribe/$', newsletter_unsubscribe, name='newsletter_unsubscribe'),
    url(r'^searchlist$', search_list_view, name='search_list'),
]