from django.contrib.auth import authenticate
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Content, User, Student, Teacher, Parent, StudentClass, Submission


# User Registration Form
class UserSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

# Student Signup Form
class StudentSignUpForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    student_class = forms.ModelChoiceField(queryset=StudentClass.objects.all(), empty_label="Select Class")
    address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Student
        fields = ['full_name', 'date_of_birth', 'student_class', 'address']

# Teacher Signup Form
class TeacherSignUpForm(forms.ModelForm):
    subject = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=15, required=False)
    years_of_experience = forms.IntegerField(min_value=0, required=True)

    class Meta:
        model = Teacher
        fields = ['full_name', 'subject', 'phone_number', 'years_of_experience']

# Parent Signup Form
class ParentSignUpForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=15)
    children = forms.ModelMultipleChoiceField(queryset=Student.objects.all(), required=True)

    class Meta:
        model = Parent
        fields = ['full_name', 'phone_number', 'children']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'fullname', 'phone', 'dob', 'address1', 'address2',
            'city', 'state', 'country', 'postal_code', 'image'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }

# class ProfilePictureForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['image']

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['subject', 'content_type', 'title', 'description', 'content_file']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            # Make 'subject' required for 'assignment' content type
            if 'content_type' in self.data and self.data.get('content_type') == 'assignment':
                self.fields['subject'].required = True
            elif 'content_type' in self.initial and self.initial.get('content_type') == 'assignment':
                self.fields['subject'].required = True

class SubmissionFeedbackForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['status', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Leave feedback for the student here...'})
        }