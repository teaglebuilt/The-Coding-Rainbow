from django.urls import path

from .views import (
	MembershipSelectView,
	PaymentView,
	updateTransactionRecords,
	my_membership_view,
	# update_profile_view,
	cancelSubscription,
	register_view,
	login_user_view,
	user_logout_view,
	)

app_name = 'memberships'

urlpatterns = [
    path('', MembershipSelectView.as_view(), name='select'),
	path('register/', register_view, name='register'),
	path('login/', login_user_view, name='login'),
	path('logout/', user_logout_view, name='logout'),
    path('payment/', PaymentView, name='payment'),
    path('update-transactions/<subscription_id>/', updateTransactionRecords, name='update-transactions'),
	path('my_membership/', my_membership_view, name='my_membership'),
	# path('update_profile/', update_profile_view, name="update_profile"),
	path('cancel/', cancelSubscription, name='cancel')
]