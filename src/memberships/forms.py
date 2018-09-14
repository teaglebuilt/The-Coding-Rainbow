from django import forms

from .models import UserMembership


class UserForm(forms.ModelForm):

    class Meta:
        model = UserMembership
        fields = ('first_name', 'last_name', 'bio',
                  'location', 'birth_date', 'avatar')


class AvatarChangeForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(
        attrs = {
            'class': 'form-control'
        }
    ))
    last_name = forms.CharField(widget=forms.TextInput(
        attrs = {
            'class': 'form-control'
        }
    ))
    location = forms.CharField(widget=forms.TextInput(
        attrs = {
            'class': 'form-control'
        }
    ))
    bio = forms.CharField(widget=forms.Textarea(
        attrs = {
            'class': 'form-control'
        }
    ))

    class Meta:
        model = UserMembership
        fields = ('avatar', 'first_name', 'last_name', 'bio', 'location')