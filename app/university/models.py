import uuid

from django.db import models
from django.conf import settings
from django.utils import timezone, dateformat


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
        default=dateformat.format(timezone.now(), 'Y-m-d')
        )
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    job = models.ForeignKey('Job', on_delete=models.PROTECT)

    def __str__(self):
        return self.user.name


class Job(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
        )
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    subjects = models.ManyToManyField('Subject', blank=True)

    def __str__(self):
        return self.user.name

class Subject(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
