from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from videoservice.utils import unique_slug_generator
from datetime import datetime
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

User = get_user_model()

MEMBERSHIP_CHOICES = (
	('Enterprise', 'ent'),
	('Professional', 'pro'),
	('Free', 'free')
)


class Membership(models.Model):
	slug = models.SlugField()
	membership_type = models.CharField(
			choices=MEMBERSHIP_CHOICES,
			default='Free',
			max_length=30)
	price = models.IntegerField(default=15)
	stripe_plan_id = models.CharField(max_length=40)

	def __str__(self):
		return self.membership_type

	class Meta:
		db_table = 'Membership'

class UserMembership(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membership')
	slug = models.SlugField()
	stripe_customer_id = models.CharField(max_length=40)
	membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True)
	first_name = models.CharField(max_length=20)
	last_name = models.CharField(max_length=20)
	bio = models.TextField(max_length=500, blank=True)
	location = models.CharField(max_length=30, blank=True)
	birth_date = models.DateField(null=True, blank=True)
	avatar = models.ImageField(upload_to='avatar', blank=True)
	friends = models.ManyToManyField("UserMembership", blank=True)


	def __str__(self):
		return self.user.username

	def get_absolute_url(self):
		return "/memberships/{}".format(self.slug)

def slug_save(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = unique_slug_generator(instance, instance.first_name)

pre_save.connect(slug_save, sender=UserMembership)

def post_save_usermembership_create(sender, instance, created, *args, **kwargs):
	if created:
		UserMembership.objects.get_or_create(user=instance)

	user_membership, created = UserMembership.objects.get_or_create(
		user=instance)
	free_membership = Membership.objects.filter(
		membership_type='Free').first()  # get the free membership instance
	if user_membership.stripe_customer_id is None or user_membership.stripe_customer_id == '':
		new_customer_id = stripe.Customer.create(email=instance.email)
		user_membership.stripe_customer_id = new_customer_id['id']
		# assign the membership of the user to the free membership on signup
		user_membership.membership = free_membership
		user_membership.save()

post_save.connect(post_save_usermembership_create,
                  sender=settings.AUTH_USER_MODEL)


class Subscription(models.Model):
	user_membership = models.ForeignKey(UserMembership, on_delete=models.CASCADE)
	stripe_subscription_id = models.CharField(max_length=40)
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.user_membership.user.username

	@property
	def get_created_date(self):
		subscription = stripe.Subscription.retrieve(self.stripe_subscription_id)
		return datetime.fromtimestamp(subscription.created)

	@property
	def get_next_billing_date(self):
		subscription = stripe.Subscription.retrieve(self.stripe_subscription_id)
		return datetime.fromtimestamp(subscription.current_period_end)

	class Meta:
		db_table = 'Subscription'


class FriendRequest(models.Model):
	to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)
	from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True) # set when created

	def __str__(self):
		return "From {}, to {}".format(self.from_user.username, self.to_user.username)