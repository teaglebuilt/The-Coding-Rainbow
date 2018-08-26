from django import forms

from .models import Course, get_membership_instance


class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = ['slug', 'title', 'description', 'image', 'allowed_membership']

    def clean(self, *args, **kwargs):
        form_data = self.cleaned_data
        free_mem = get_membership_instance('Free')
        ent_mem = get_membership_instance('Ent')

        # if the non-free memberships are allowed, add the free membership
        if form_data['allowed_membership'].count() >= 1:
            if free_mem not in form_data['allowed_membership'].all():
                raise forms.ValidationError(
                    "The Free membership should be allowed too!")
