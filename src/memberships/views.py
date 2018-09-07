from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.views.generic import ListView
from django.urls import reverse
from blog.models import Post
from allauth.account.views import SignupView, LoginView
from .models import Membership, UserMembership, Subscription, FriendRequest
from .forms import UserForm, AvatarChangeForm
import stripe

User = get_user_model()

@login_required
def user_logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def my_membership_view(request):
    user_membership = get_user_membership(request)
    user_subscription = get_user_subscription(request)
    user_posts = Post.objects.filter(author=user_membership)

    p = UserMembership.objects.filter(user=request.user).first()
    sent_friend_requests = FriendRequest.objects.filter(from_user=p.user)
    rec_friend_requests = FriendRequest.objects.filter(to_user=p.user)



    avatar_form = AvatarChangeForm()
    if request.method == "POST":
        avatar_form = AvatarChangeForm(request.POST, request.FILES)
        if avatar_form.is_valid():
            user_membership.avatar = avatar_form.cleaned_data.get('avatar')
            user_membership.first_name = avatar_form.cleaned_data.get('first_name')
            user_membership.last_name = avatar_form.cleaned_data.get('last_name')
            user_membership.bio = avatar_form.cleaned_data.get('bio')
            user_membership.location = avatar_form.cleaned_data.get('location')
            user_membership.save()
    context = {
		'user_membership': user_membership,
        'sent_friend_requests': sent_friend_requests,
        'rec_friend_requests': rec_friend_requests,
        'user_subscription': user_subscription,
        'posts': user_posts,
        'avatar_form': avatar_form
    }
    return render(request, "memberships/my_membership.html", context)


def get_user_membership(request):
    user_membership_qs = UserMembership.objects.filter(user=request.user)
    if user_membership_qs.exists():
        return user_membership_qs.first()
    return None


def get_user_subscription(request):
    user_subscription_qs = Subscription.objects.filter(
        user_membership=get_user_membership(request))  # FK on Subscription
    if user_subscription_qs.exists():
        user_subscription = user_subscription_qs.first()
        return user_subscription
    return None


def get_selected_membership(request):
    membership_type = request.session['selected_membership_type']
    selected_membership_qs = Membership.objects.filter(
        membership_type=membership_type)
    if selected_membership_qs.exists():
        return selected_membership_qs.first()
    return None


class MembershipSelectView(ListView):
    model = Membership

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        current_membership = get_user_membership(self.request)
        context['current_membership'] = str(current_membership.membership)
        return context

    def post(self, request, **kwargs):
        user_membership = get_user_membership(request)
        user_subscription = get_user_subscription(request)

        selected_membership_type = request.POST.get('membership_type')

        selected_membership_qs = Membership.objects.filter(
            membership_type=selected_membership_type)
        print(selected_membership_qs)
        selected_membership = selected_membership_qs.first()
        print(selected_membership)

        if user_membership.membership == selected_membership:
            if user_subscription is None:
                messages.info(request, "You already have this membership. Your \
					next payment is due {}".format('get this value from stripe'))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # assign to the session
        # Membership field
        request.session['selected_membership_type'] = selected_membership.membership_type

        return HttpResponseRedirect(reverse('memberships:payment'))


def PaymentView(request):

    user_membership = get_user_membership(request)

    selected_membership = get_selected_membership(request)

    publishKey = settings.STRIPE_PUBLISHABLE_KEY

    if request.method == "POST":
        try:
            token = request.POST['stripeToken']
            subscription = stripe.Subscription.create(
                customer=user_membership.stripe_customer_id,  # id on User Membership Model
                items=[
                    {
                        "plan": selected_membership.stripe_plan_id,
                    },
                ],
                trial_period_days=100
            )

            return redirect(reverse('memberships:update-transactions',
                                    kwargs={
                                        'subscription_id': subscription.id
                                    }))

        except stripe.error.CardError as e:
            messages.info(request, "Your card has been declined")

    context = {
        'publishKey': publishKey,
        'selected_membership': selected_membership
    }

    return render(request, "memberships/membership_payment.html", context)


def updateTransactionRecords(request, subscription_id):
    user_membership = get_user_membership(request)
    selected_membership = get_selected_membership(request)

    user_membership.membership = selected_membership
    user_membership.save()

    sub, created = Subscription.objects.get_or_create(
        user_membership=user_membership)
    sub.stripe_subscription_id = subscription_id
    sub.active = True
    sub.save()

    try:
        del request.session['selected_membership_type']
    except:
        pass

    messages.info(request, 'Successfully created {} membership'.format(
        selected_membership))
    return redirect('/memberships')


def cancelSubscription(request):
    user_sub = get_user_subscription(request)

    if user_sub.active is False:
        messages.info(request, "You dont have an active membership")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    sub = stripe.Subscription.retrieve(user_sub.stripe_subscription_id)
    sub.delete()

    user_sub.active = False
    user_sub.save()

    free_membership = Membership.objects.filter(membership_type='Free').first()
    user_membership = get_user_membership(request)
    user_membership.membership = free_membership
    user_membership.save()

    messages.info(
        request, "Successfully cancelled membership. We have sent an email")
    # sending an email here

    return redirect('/memberships')


def users_list(request):
    users = UserMembership.objects.exclude(user=request.user)
    context = { 'users': users }
    return render(request, 'memberships/users_list.html', context)


def send_friend_request(request, id):
	if request.user.is_authenticated:
		user = get_object_or_404(User, id=id)
		frequest, created = FriendRequest.objects.get_or_create(
			from_user=request.user,
			to_user=user)
		return HttpResponseRedirect('/memberships')

def cancel_friend_request(request, id):
	if request.user.is_authenticated:
		user = get_object_or_404(User, id=id)
		frequest = FriendRequest.objects.filter(
			from_user=request.user,
			to_user=user).first()
		frequest.delete()
		return HttpResponseRedirect('/memberships/my_membership')

def accept_friend_request(request, id):
	from_user = get_object_or_404(User, id=id)
	frequest = FriendRequest.objects.filter(from_user=from_user, to_user=request.user).first()
	user1 = frequest.to_user
	user2 = from_user
	user1.profile.friends.add(user2.profile)
	user2.profile.friends.add(user1.profile)
	frequest.delete()
	return HttpResponseRedirect('/memberships/{}'.format(request.user.profile.slug))


def delete_friend_request(request, id):
	from_user = get_object_or_404(User, id=id)
	frequest = FriendRequest.objects.filter(from_user=from_user, to_user=request.user).first()
	frequest.delete()
	return HttpResponseRedirect('/memberships/{}'.format(request.user.profile.slug))


def profile_view(request, slug):
    p = UserMembership.objects.filter(slug=slug).first()
    u = p.user
    user_membership = UserMembership.objects.filter(slug=slug).first()
    sent_friend_requests = FriendRequest.objects.filter(from_user=p.user)
    rec_friend_requests = FriendRequest.objects.filter(to_user=p.user)

    friends = p.friends.all()

    # is this user our friend?
    button_status = 'none'
    if p not in friends.all():
        button_status = 'not_friend'

        # if we have sent him a friend request
        if len(FriendRequest.objects.filter(
            from_user=request.user).filter(to_user=p.user)) == 1:
                button_status = 'friend_request_sent'

    context = {
        'user_membership': user_membership,
        'u': u,
        'button_status': button_status,
        'friends': friends,
        'sent_friends_requests': sent_friend_requests,
        'rec_friend_requests': rec_friend_requests
    }

    return render(request, "memberships/profile_view.html", context)



