from django.urls import path
from django.conf.urls import url
from .views import posts_list


app_name = 'blog'


urlpatterns = [
    url(r'^$', posts_list),
]