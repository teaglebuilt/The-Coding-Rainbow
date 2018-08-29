from django.urls import path
from allauth.account.views import LoginView, SignupView
from .views import (
	MembershipSelectView,
	PaymentView,
	updateTransactionRecords,
	my_membership_view,
	# update_profile_view,
	cancelSubscription,
	user_logout_view,
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
	# path('update_profile/', update_profile_view, name="update_profile"),
	path('cancel/', cancelSubscription, name='cancel')
]