from django.contrib.auth.models import User
from django import forms
from .models import Post


class PostModelForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(
        attrs = {
            'class': 'form-control'
        }
    ))
    description = forms.CharField(widget=forms.Textarea(
        attrs = {
            'class': 'form-control'
        }
    ))

    class Meta:
        model = Post
        fields = ('title', 'description', 'image')