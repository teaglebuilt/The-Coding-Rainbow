from django.contrib.auth.models import User
from django import forms
from pagedown.widgets import PagedownWidget
from memberships.models import UserMembership
from .models import Post, NewsLetterUser
from crispy_forms.helper import FormHelper


class PostModelForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(
        attrs = {
            'class': 'form-control'
        }
    ))
    description = forms.CharField(widget=PagedownWidget)

    class Meta:
        model = Post
        fields = ('title', 'description', 'image')


class SearchForm(forms.ModelForm):

    class Meta:
        model = UserMembership
        fields = ('user',)

    def __init__(self, search_term, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['search'].queryset = UserMembership.objects.filter(exclude=request.user)


class NewsLetterSignUpForm(forms.ModelForm):

    class Meta:
        model = NewsLetterUser
        fields = ('email',)

        def clean_email(self):
            email = self.cleaned_data.get('email')
            return email