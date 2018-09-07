from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from .models import Course, Lesson
from memberships.models import UserMembership
# Create your views here.

class CourseListView(ListView):
    model = Course


class CourseDetailView(DetailView):
    model = Course

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lesson'] = Lesson.objects.all()
        return context



class LessonDetailView(View):
 # filter all the courses, and then filter that course's lessons for a specific lesson..yeah wtf
    def get(self, request, course_slug, lesson_slug, *args, **kwargs):

        course_queryset = Course.objects.filter(slug=course_slug)
        if course_queryset.exists():
            course = course_queryset.first()

        lesson_queryset = course.lessons.filter(slug=lesson_slug)
        if lesson_queryset.exists():
            lesson = lesson_queryset.first()

        user_membership = UserMembership.objects.filter(user=request.user).first()
        user_membership_type = user_membership.membership.membership_type #membership types

        course_allowed_mem_types = course.allowed_membership.all()
         # MAny to Many -allowed memberships

        context = {
            'object': None
        }

        # check to see lesson available for the user's membership type
        # how can i can i pass the membership choice with free included?
        if course_allowed_mem_types.filter(membership_type=user_membership_type).exists():
            context = {'object': lesson }


        return render(request, 'courses/lesson_detail.html', context)