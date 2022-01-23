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

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            password = user_data.pop('password', None)
            get_user_model().objects.filter(id=instance.user.id).update(
                    **user_data
                )
            user = get_user_model().objects.get(id=instance.user.id)
            if password:
                user.set_password(password)
                user.save()
            validated_data['user'] = user

        models.Employee.objects.filter(
            id=instance.id
        ).update(**validated_data)

        return instance


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

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        subjects = validated_data.pop('subjects', None)
        if user_data:
            password = user_data.pop('password', None)
            get_user_model().objects\
                .filter(id=instance.user.id).update(
                    **user_data
                )
            user = get_user_model().objects.get(id=instance.user.id)
            if password:
                user.set_password(password)
                user.save()
            validated_data['user'] = user

        models.Teacher.objects.filter(
            id=instance.id
        ).update(**validated_data)

        if subjects:
            instance.subjects.set(subjects)
            instance.save()

        return instance


class CourseSerializer(serializers.ModelSerializer):
    subjects = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Subject.objects.all()
    )

    class Meta:
        model = models.Course
        fields = ('id', 'name', 'subjects')
        extra_kwargs = {'id': {'read_only': True}}


class SubjectFilteredPrimaryKeyRelatedField(
        serializers.PrimaryKeyRelatedField):
    """Filter queryset of lessons on browsable api"""
    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = super(SubjectFilteredPrimaryKeyRelatedField, self)\
            .get_queryset()
        if not request or not queryset:
            return None
        teacher = models.Teacher.objects.get(user__email=request.user.email)
        queryset = teacher.subjects.all()
        return queryset


class LessonSerializer(serializers.ModelSerializer):
    subject = SubjectFilteredPrimaryKeyRelatedField(
        queryset=models.Subject.objects.all()
    )

    class Meta:
        model = models.Lesson
        fields = ('id', 'title', 'textual_content', 'video_url', 'subject')
        extra_kwargs = {'id': {'read_only': True}}

    def validate(self, attrs):
        request = self.context.get('request', None)
        if not request:
            return None
        subject = attrs['subject']
        user = request.user
        teacher = models.Teacher.objects.get(user__email=user.email)
        subject_set = teacher.subjects.all()
        if subject not in subject_set:
            raise serializers.ValidationError(
                "The teacher cannot assign a lesson to a\
                subject he does not teach"
                )
        return super().validate(attrs)
