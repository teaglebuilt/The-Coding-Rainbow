from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout, login, authenticate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView, ListView
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext

from .models import Post, NewsLetterUser
from memberships.models import UserMembership
from memberships.views import get_user_membership
from .forms import PostModelForm, NewsLetterSignUpForm


def search_list_view(request):
    search_query = request.GET.get('search')
    search_results = UserMembership.objects.filter(user__username__icontains=search_query)
    print(search_results)
    return render(request, 'blog/posts_list.html', {'search_results': search_results})



def posts_list(request):
    queryset_list = Post.objects.all().order_by("-timestamp")
    users = UserMembership.objects.exclude(user=request.user)
    query = request.GET.get('q')
    if query:
        queryset_list = queryset_list.filter(
            Q(title__icontains=query)
            ).distinct()
    paginator = Paginator(queryset_list, 3)
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    # get the last 3 posts
    recent_posts = Post.objects.order_by('-timestamp')[0:3]

    context = {
        'users': users,
        'all_posts': queryset,
        'page_request_var': page_request_var,
        'recent_posts': recent_posts
    }
    return render(request, 'blog/posts_list.html', context)


def post_detail(request, slug):
    user = UserMembership.objects.filter(user=request.user)[0]
    instance = get_object_or_404(Post, slug=slug)

    context = {
        'user': user,
        'instance': instance
    }
    return render(request, 'blog/posts_detail.html', context)


class PostLikeToggle(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        slug = self.kwargs.get('slug')
        obj = get_object_or_404(Post, slug=slug)
        url_ = obj.get_absolute_url()
        user = obj.author
        if user:
            if user in obj.likes.all():
                obj.likes.remove(user)
            else:
                obj.likes.add(user)
        return url_


class PostLikeAPIToggle(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, slug=None, format=None):
        # slug = self.kwargs.get('slug')
        obj = get_object_or_404(Post, slug=slug)
        url_ = obj.get_absolute_url()
        user = get_user_membership(request)
        updated = False
        liked = False
        if user.user.is_authenticated:
            if user in obj.likes.all():
                liked = False
                updated = True
                obj.likes.remove(user)
            else:
                liked = True
                obj.likes.add(user)
                updated = True
        data = {
            "updated": updated,
            "liked": liked
        }

        return Response(data)


@login_required
def post_create(request):
    form = PostModelForm()
    if request.POST:
        form = PostModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.author = get_user_membership(request)
            form.instance.save()
        post = get_object_or_404(Post, slug=form.instance.slug)
        return redirect(post.get_absolute_url())

    context = {'form': form}
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
    return redirect('blog:blog')


def newsletter_signup(request):
    if request.method == 'POST':
        form = NewsLetterSignUpForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            if NewsLetterUser.objects.filter(email=instance.email).exists():
                messages.warning(request, 'Your email already exists.')
            else:
                instance.save()
    else:

        form = NewsLetterSignUpForm()

        return render(request, 'blog/posts_list.html', {'form': form})

def newsletter_unsubscribe(request):
    form = NewsLetterSignUpForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        if NewsLetterUser.objects.filter(email=instance.email).exists():
            NewsLetterUser.objects.filter(email.instance.email).delete()
        else:
            print('Sorry, we did not find your email address.')

        context = {
            'form': form
        }
        template = 'blog/unsubscribe.html'
        return render(request, template, context)