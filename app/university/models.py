import uuid
import datetime

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class Employee(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False
        )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
        )

    hired_date = models.DateField(
        default=datetime.date.today
        )
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    job = models.ForeignKey('Job', on_delete=models.PROTECT)

    def __str__(self):
        return self.user.name


class Job(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False
        )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False
        )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
        )
    hired_date = models.DateField(
        default=datetime.date.today
        )
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    subjects = models.ManyToManyField('Subject', blank=True)

    def __str__(self):
        return self.user.name


class Subject(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False
        )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Course(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False
        )
    name = models.CharField(max_length=255)
    subjects = models.ManyToManyField(Subject, blank=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False
        )
    title = models.CharField(max_length=255)
    textual_content = models.TextField()
    video_url = models.URLField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    # pdf = models.FileField(blank=True)
    # featured_image = models.ImageField(upload_to='images/%Y/%m')

    def __str__(self):
        return self.title


class Student(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False
        )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
        )
    course = models.ForeignKey(Course, on_delete=models.PROTECT)

    def __str__(self):
        return self.user.name


# Signals
def add_employee_to_group(sender, instance, created, **kwargs):
    if created:
        user = get_user_model().objects.get(email=instance.user.email)
        group, created_bool = Group.objects.get_or_create(name='School Admin')

        user.groups.add(group.id)
        user.save()


def add_teacher_to_group(sender, instance, created, **kwargs):
    if created:
        user = get_user_model().objects.get(email=instance.user.email)
        group, created_bool = Group.objects.get_or_create(name='Teachers')

        user.groups.add(group.id)
        user.save()


post_save.connect(add_employee_to_group, sender=Employee)
post_save.connect(add_teacher_to_group, sender=Teacher)
