from django.db import models
from memberships.models import Membership
from django.urls import reverse


class Course(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=120)
    description = models.TextField()
    image = models.ImageField(null=True, blank=True)
    allowed_membership = models.ManyToManyField(Membership)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('courses:detail', kwargs={'slug': self.slug})

    @property
    def lessons(self): # grouping lessons with a course in a specific order
        return self.lesson_set.all().order_by('position')

    class Meta:
        db_table = 'Course'

class Lesson(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=120)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    position = models.IntegerField()
    video_url = models.FileField(upload_to='videos/%Y/%m/$D/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='images/%Y/%m/$D/', null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('courses:lesson-detail', kwargs={'course_slug': self.course.slug, 'lesson_slug': self.slug})

    class Meta:
        db_table = 'Lesson'
