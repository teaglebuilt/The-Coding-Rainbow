from django.contrib import admin
from .forms import CourseForm
from .models import Course, Lesson


# class CourseAdmin(admin.ModelAdmin):
#     form = CourseForm


admin.site.register(Course)
admin.site.register(Lesson)