from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.db.models import F
from grades.models import Grade
from django.apps import apps  


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
    is_teacher = models.BooleanField(default=False)

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
    assigned_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True, related_name="teachers")
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
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=50, choices=[('lecture', 'Lecture'), ('assignment', 'Assignment'), ('note', 'Note')])
    title = models.CharField(max_length=255)
    description = RichTextField()
    content_file = models.FileField(upload_to='uploads/', blank=True, null=True)
    date_uploaded = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.date_uploaded})"
    



class Submission(models.Model):
    # Fields remain the same
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="submissions", null=True, blank=True)
    answer = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, 
        choices=[('correct', 'Correct'), ('incorrect', 'Incorrect'), ('pending', 'Pending')], 
        default='pending'
    )
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Submission by {self.student.full_name} for {self.content.title}"

    def save(self, *args, **kwargs):
        # Check if the status has changed
        previous_status = None
        if self.pk:
            previous_status = Submission.objects.get(pk=self.pk).status
        
        super().save(*args, **kwargs)  # Save the submission first

        # Lazy load the Grade model
        Grade = apps.get_model('grades', 'Grade')
        grade, created = Grade.objects.get_or_create(student=self.student, subject=self.subject)

        if self.status == 'correct':
            grade.score = min(100, grade.score + 5)  # Add 5 points, cap at 100
        elif self.status == 'incorrect' and previous_status != 'incorrect':
            grade.score -= 10  # Deduct 10 points
        elif self.status == 'pending' and previous_status == 'correct':
            grade.score -= 5  # Revert the 5 points added for correct

        grade.save()


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="attendances")
    content = models.ForeignKey('Content', on_delete=models.CASCADE, related_name="attendances")  # Link to content
    attended = models.BooleanField(default=False)  # True if attended, False if absent
    attendance_points = models.IntegerField(default=0)  # Default 0, 5 points if attended
    timestamp = models.DateTimeField(auto_now_add=True)  # To store when attendance was marked

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name} - {'Attended' if self.attended else 'Absent'}"
    


class Event(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teacher_events", null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_general = models.BooleanField(default=False)  # Whether this is a general event visible to all students
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
    
    
class Material(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='materials/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    


class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)

    def __str__(self):
        return self.name
    
class StudentReport(models.Model):
    GRADE_CHOICES = [
        ('Distinction', 'Distinction'),
        ('Credit', 'Credit'),
        ('Merit', 'Merit'),
        ('Pass', 'Pass'),
        ('Failure', 'Failure'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    total_average = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    overall_grade = models.CharField(max_length=20, choices=GRADE_CHOICES, default='Failure')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Report for {self.student.full_name} - {self.school.name}"
    
class SubjectGrade(models.Model):
    report = models.ForeignKey(StudentReport, on_delete=models.CASCADE, related_name='subject_grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 75.50 for a grade
    attendance = models.PositiveIntegerField()  # e.g., 90 for 90% attendance

    def __str__(self):
        return f"{self.subject.name} - {self.report.student.fullname}"

# Signal to calculate total average and grade
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=SubjectGrade)
def calculate_report_average(sender, instance, **kwargs):
    report = instance.report
    grades = report.subject_grades.all()
    total_grade = sum([grade.grade for grade in grades])
    total_subjects = grades.count()
    report.total_average = total_grade / total_subjects if total_subjects > 0 else 0.0

    # Determine overall grade based on the average
    if report.total_average >= 75:
        report.overall_grade = 'Distinction'
    elif report.total_average >= 65:
        report.overall_grade = 'Credit'
    elif report.total_average >= 50:
        report.overall_grade = 'Merit'
    elif report.total_average >= 40:
        report.overall_grade = 'Pass'
    else:
        report.overall_grade = 'Failure'

    report.save()