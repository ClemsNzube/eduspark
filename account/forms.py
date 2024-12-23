from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Student, Teacher, Parent

# User Registration Form
class UserSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.RadioSelect(), required=True)

    class Meta:
        model = User
        fields = ['email', 'role', 'password1', 'password2']

# Student Signup Form
class StudentSignUpForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    student_class = forms.ChoiceField(choices=[('1', 'Class 1'), ('2', 'Class 2'), ('3', 'Class 3'), 
                                               ('4', 'Class 4'), ('5', 'Class 5'), ('6', 'Class 6')])
    address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Student
        fields = ['full_name', 'date_of_birth', 'student_class', 'address']

# Teacher Signup Form
class TeacherSignUpForm(forms.ModelForm):
    subject = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = Teacher
        fields = ['full_name', 'subject', 'phone_number']

# Parent Signup Form
class ParentSignUpForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=15)
    children = forms.ModelMultipleChoiceField(queryset=Student.objects.all(), required=True)

    class Meta:
        model = Parent
        fields = ['full_name', 'phone_number', 'children']
