from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.views.generic import ListView
from django.urls import reverse
from blog.models import Author
from .models import Membership, UserMembership, Subscription
from .forms import UserForm, UpdateUserForm
import stripe


def register_view(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True

        return login_user_view(request)

    elif request.method == 'GET':
        user_form = UserForm()
        template_name = 'memberships/register.html'
        return render(request, template_name, {'user_form': user_form})

def login_user_view(request):
    context = RequestContext(request)

    if request.method == 'POST':

        username=request.POST['username']
        password=request.POST['password']
        authenticated_user = authenticate(username=username, password=password)

        if authenticated_user is not None:
            login(request=request, user=authenticated_user)
            return HttpResponseRedirect('/courses/')

        else:

            print("Invalid login details: {}, {}".format(username, password))
            return HttpResponse("Invalid login details supplied.")


    return render(request, 'memberships/login.html', {}, context)

@login_required
def user_logout_view(request):
    logout(request)
    return HttpResponseRedirect('memberships/login')



def my_membership_view(request):
	user_membership = get_user_membership(request)
	user_subscription = get_user_subscription(request)
	context = {
		'user_membership': user_membership,
		'user_subscription': user_subscription
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
        '''
		==========
		VALIDATION
		==========
		'''

        if user_membership.membership == selected_membership:
            if user_subscription != None:
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
				trial_period_days= 100
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

	if user_sub.active == False:
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

	messages.info(request, "Successfully cancelled membership. We have sent an email")
	# sending an email here

	return redirect('/memberships')