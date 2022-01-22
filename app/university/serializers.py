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
            user = instance.user
            if 'name' in user_data.keys():
                user.name = user_data['name']
            if 'email' in user_data.keys():
                user.email = user_data['email']
            if 'password' in user_data.keys():
                user.set_password(user_data['password'])
            if 'cpf' in user_data.keys():
                user.cpf = user_data['cpf']
            if 'phone' in user_data.keys():
                user.phone = user_data['phone']
            if 'street' in user_data.keys():
                user.street = user_data['street']
            if 'state' in user_data.keys():
                user.state = user_data['state']
            if 'city' in user_data.keys():
                user.city = user_data['city']
            if 'zip_code' in user_data.keys():
                user.zip_code = user_data['zip_code']
            if 'complement' in user_data.keys():
                user.complement = user_data['complement']
            user.save()
            instance.user = user
        
        if 'hired_date' in validated_data.keys():
            instance.hired_date = validated_data['hired_date']
        
        if 'job' in validated_data.keys():
            instance.job = validated_data['job']
        
        if 'salary' in validated_data.keys():
            instance.salary = validated_data['salary']        
        instance.save()
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
