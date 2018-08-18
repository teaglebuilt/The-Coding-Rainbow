from django.urls import path

from .views import (
	MembershipSelectView,
	PaymentView,
	updateTransactionRecords,
	my_membership_view,
	cancelSubscription
	)

app_name = 'memberships'

urlpatterns = [
    path('', MembershipSelectView.as_view(), name='select'),
    path('payment/', PaymentView, name='payment'),
    path('update-transactions/<subscription_id>/', updateTransactionRecords, name='update-transactions'),
	path('my_membership/', my_membership_view, name='my_membership'),
	path('cancel/', cancelSubscription, name='cancel')
]