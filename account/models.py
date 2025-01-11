from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
    ]

    # Remove the default username field
    username = None
    email = models.EmailField(unique=True)

    # Custom fields
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    fullname = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # Override group and permissions fields to avoid conflicts
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"
    
class StudentClass(models.Model):
    name = models.CharField(max_length=100)  # e.g., "Grade 1", "Class 6"
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name



class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField()
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)  # Link to StudentClass
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.student_class.name}"



class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    subject = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    years_of_experience = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.full_name} - {self.subject}"


class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    children = models.ManyToManyField(Student, related_name='parents')

    def __str__(self):
        return self.full_name
    


class Subject(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Timetable(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=100)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)  # ForeignKey to StudentClass

    def __str__(self):
        return f"{self.subject.name} by {self.teacher.full_name} for {self.student_class.name} on {self.day_of_week} from {self.start_time} to {self.end_time}"



class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Content(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=50, choices=[('lecture', 'Lecture'), ('assignment', 'Assignment'), ('note', 'Note')])
    title = models.CharField(max_length=255)
    description = RichTextField()
    content_file = models.FileField(upload_to='uploads/', blank=True, null=True)
    date_uploaded = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.date_uploaded})"