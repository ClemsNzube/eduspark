from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserSignUpForm, StudentSignUpForm, TeacherSignUpForm, ParentSignUpForm
from .models import User, Student, Teacher, Parent

# Sign up view for User (Student, Teacher, Parent)
def user_signup(request):
    if request.method == 'POST':
        user_form = UserSignUpForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            role = user.role
            if role == 'student':
                student_form = StudentSignUpForm(request.POST)
                if student_form.is_valid():
                    student = student_form.save(commit=False)
                    student.user = user
                    student.save()
            elif role == 'teacher':
                teacher_form = TeacherSignUpForm(request.POST)
                if teacher_form.is_valid():
                    teacher = teacher_form.save(commit=False)
                    teacher.user = user
                    teacher.save()
            elif role == 'parent':
                parent_form = ParentSignUpForm(request.POST)
                if parent_form.is_valid():
                    parent = parent_form.save(commit=False)
                    parent.user = user
                    parent.save()
            
            login(request, user)
            messages.success(request, f'Account created for {user.email}!')
            return redirect('home')
    else:
        user_form = UserSignUpForm()
        student_form = StudentSignUpForm()
        teacher_form = TeacherSignUpForm()
        parent_form = ParentSignUpForm()

    return render(request, 'signup.html', {
        'user_form': user_form,
        'student_form': student_form,
        'teacher_form': teacher_form,
        'parent_form': parent_form,
    })

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Password Reset View
def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            messages.success(request, 'Password reset link sent to your email.')
            return redirect('login')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset.html', {'form': form})

# Home page view (for logged-in users)
@login_required
def home(request):
    return render(request, 'home.html')
