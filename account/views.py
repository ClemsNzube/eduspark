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
    role = request.GET.get('role')  # Get the role from the URL query parameters
    if not role:
        # If no role is selected, redirect or show an error message
        messages.error(request, "Please select a role before signing up.")
        return redirect('home')  # Redirect to the home page or role selection

    if request.method == 'POST':
        # Handle the form submission based on the selected role
        user_form = UserSignUpForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.role = role  # Set the role from the URL parameter

            # Handle the role-specific form based on the selected role
            if role == 'student':
                student_form = StudentSignUpForm(request.POST)
                if student_form.is_valid():
                    student = student_form.save(commit=False)
                    student.user = user  # Link the student to the user
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

            # Log the user in after successful signup
            login(request, user)
            messages.success(request, f'Account created for {user.email}!')
            
            # Redirect based on role
            if role == 'student':
                return redirect('student_dashboard')
            elif role == 'teacher':
                return redirect('teacher_dashboard')
            elif role == 'parent':
                return redirect('parent_dashboard')
            else:
                return redirect('home')

    else:
        # Instantiate empty forms
        user_form = UserSignUpForm()
        student_form = StudentSignUpForm()
        teacher_form = TeacherSignUpForm()
        parent_form = ParentSignUpForm()

    return render(request, 'home/stu-signup.html', {
        'user_form': user_form,
        'student_form': student_form,
        'teacher_form': teacher_form,
        'parent_form': parent_form,
        'role': role,  # Pass the selected role to the template
    })


# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirect based on role
            if user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'teacher':
                return redirect('teacher_dashboard')
            elif user.role == 'parent':
                return redirect('parent_dashboard')
            else:
                return redirect('home')  # Fallback for unexpected roles
    else:
        form = AuthenticationForm()
    
    return render(request, 'home/login.html', {'form': form})


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
    return render(request, 'home/index.html')
