from django.urls import path
from django.conf.urls import url
from allauth.account.views import LoginView, SignupView
from .views import (
	MembershipSelectView,
	PaymentView,
	updateTransactionRecords,
	my_membership_view,
	cancelSubscription,
	user_logout_view,
	profile_view,
	accept_friend_request,
	send_friend_request,
	delete_friend_request,
	cancel_friend_request,
	delete_friend,
	)

app_name = 'memberships'

urlpatterns = [
    path('', MembershipSelectView.as_view(), name='select'),
	path('signup/', SignupView.as_view(), name='signup'),
	path('login/', LoginView.as_view(), name='login'),
	path('logout/', user_logout_view, name='logout'),
    path('payment/', PaymentView, name='payment'),
    path('update-transactions/<subscription_id>/', updateTransactionRecords, name='update-transactions'),
	path('my_membership/', my_membership_view, name='my_membership'),
	path('cancel/', cancelSubscription, name='cancel'),
	url(r'^(?P<slug>[\w-]+)/$', profile_view, name='profile-view'),
	url(r'^friend-request/send/(?P<id>[\w-]+)/$', send_friend_request),
    url(r'^friend-request/cancel/(?P<id>[\w-]+)/$', cancel_friend_request),
    url(r'^friend-request/accept/(?P<id>[\w-]+)/$', accept_friend_request),
    url(r'^friend-request/delete/(?P<id>[\w-]+)/$', delete_friend_request),
	url(r'^friends/delete/(?P<id>[\w-]+)/$', delete_friend),
]