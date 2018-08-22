from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from .models import Post, Author
from .forms import PostModelForm

# Create your views here.
def posts_list(request):
    all_posts = Post.objects.all()
    context = {
        'all_posts': all_posts
    }
    return render(request, 'blog/posts_list.html', context)


def create_post_view(request):
    # author, created = Author.objects.get_or_create(
    #     user=request.user,
    #     name=request.user.first_name,
    #     membership= author.membership.membership_type)
    form = PostModelForm(request.POST or None, request.FILES or None)
    if form.is_valid():
       form.instance.author = author
       form.save()
       messages.info(request, 'Successfully created a new blog post!')
       return redirect('/blog/')

    context = {
        'form': form
    }
    return render(request, "blog/create_post.html", context)