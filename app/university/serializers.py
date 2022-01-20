from django.contrib.auth import get_user_model

from rest_framework import serializers
from university import models

from accounts.serializers import UserSerializer


class EmployeeSerializer(serializers.ModelSerializer):
    job = serializers.PrimaryKeyRelatedField(queryset=models.Job.objects.all())
    user = UserSerializer()

    class Meta:
        model = models.Employee
        fields = ('id', 'user', 'hired_date', 'salary', 'job')
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = get_user_model().objects.create_user(**user_data)
        employee = models.Employee.objects.create(**validated_data, user=user)
        return employee


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    subjects = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Subject.objects.all()
    )

    class Meta:
        model = models.Teacher
        fields = ('id', 'user', 'hired_date', 'salary', 'subjects')
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        subjects = validated_data.pop('subjects')
        user = get_user_model().objects.create_user(**user_data)
        teacher = models.Teacher.objects.create(**validated_data, user=user)
        teacher.subjects.set(subjects)
        return teacher


class CourseSerializer(serializers.ModelSerializer):
    subjects = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Subject.objects.all()
    )

    class Meta:
        model = models.Course
        fields = ('id', 'name', 'subjects')
        extra_kwargs = {'id': {'read_only': True}}
