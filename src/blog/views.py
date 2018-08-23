from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout, login, authenticate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from .models import Post, Author
from .forms import PostModelForm


# Create your views here.
def posts_list(request):
    queryset_list = Post.objects.all()
    paginator = Paginator(queryset_list, 3)
    page = request.GET.get("page")
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    context = {
        'object_list': queryset
    }
    return render(request, 'blog/posts_list.html', context)


def post_detail(request, slug):
    instance = get_object_or_404(Post, slug=slug)
    context = {
        'instance': instance
    }
    return render(request, 'blog/posts_detail.html', context)


def create_post(request):
    author, created = Author.objects.get_or_create(
        user=request.user)
    form = PostModelForm(request.POST or None, request.FILES or None)
    if form.is_valid():
       form.instance.author = author
       form.save()
       return redirect('/blog/')

    context = {

        'form': form
    }
    return render(request, "blog/create_post.html", context)

def post_update(request, slug):
	unique_post = get_object_or_404(Post, slug=slug)
	form = PostModelForm(request.POST or None,
						request.FILES or None,
						instance=unique_post)
	if form.is_valid():
		form.save()
		return redirect('/blog/')

	context = {
		'form': form
	}
	return render(request, "blog/create_post.html", context)



def post_delete(request, slug):
    unique_post = get_object_or_404(Post, slug=slug)
    unique_post.delete()
    return redirect('/blog/')