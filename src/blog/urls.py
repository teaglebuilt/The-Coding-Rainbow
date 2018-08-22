from django.urls import path
from django.conf.urls import url
from .views import posts_list, create_post_view


app_name = 'blog'


urlpatterns = [
    url(r'^$', posts_list),
    url(r'^create/$', create_post_view),
]