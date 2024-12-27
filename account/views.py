from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm
from .forms import CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
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

    # Initialize role-specific forms
    student_form = None
    teacher_form = None
    parent_form = None

    if request.method == 'POST':
        # Handle the user signup form
        user_form = UserSignUpForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.role = role  # Set the role from the URL parameter
            user.save()  # Save the user instance

            # Check if the user already has a profile for the selected role
            if role == 'student' and Student.objects.filter(user=user).exists():
                messages.error(request, "This user already has a student profile.")
                return redirect('home')  # Redirect if the user already has a student profile
            
            elif role == 'teacher' and Teacher.objects.filter(user=user).exists():
                messages.error(request, "This user already has a teacher profile.")
                return redirect('home')  # Redirect if the user already has a teacher profile
            
            elif role == 'parent' and Parent.objects.filter(user=user).exists():
                messages.error(request, "This user already has a parent profile.")
                return redirect('home')  # Redirect if the user already has a parent profile

            # Role-specific form handling
            if role == 'student':
                student_form = StudentSignUpForm(request.POST)
                if student_form.is_valid():
                    student = student_form.save(commit=False)
                    student.user = user  # Link the student to the user
                    student.full_name = student_form.cleaned_data.get('full_name')
                    student.date_of_birth = student_form.cleaned_data.get('date_of_birth')
                    student.student_class = student_form.cleaned_data.get('student_class')
                    student.address = student_form.cleaned_data.get('address')
                    student.save()

            elif role == 'teacher':
                teacher_form = TeacherSignUpForm(request.POST)
                if teacher_form.is_valid():
                    teacher = teacher_form.save(commit=False)
                    teacher.user = user
                    teacher.full_name = teacher_form.cleaned_data.get('full_name')
                    teacher.subject = teacher_form.cleaned_data.get('subject')
                    teacher.phone_number = teacher_form.cleaned_data.get('phone_number')
                    teacher.years_of_experience = teacher_form.cleaned_data.get('years_of_experience')
                    teacher.save()

            elif role == 'parent':
                parent_form = ParentSignUpForm(request.POST)
                if parent_form.is_valid():
                    parent = parent_form.save(commit=False)
                    parent.user = user
                    parent.full_name = parent_form.cleaned_data.get('full_name')
                    parent.phone_number = parent_form.cleaned_data.get('phone_number')
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
        # Initialize role-specific forms
        user_form = UserSignUpForm()
        if role == 'student':
            student_form = StudentSignUpForm()
        elif role == 'teacher':
            teacher_form = TeacherSignUpForm()
        elif role == 'parent':
            parent_form = ParentSignUpForm()

    # Render the signup template with the relevant forms
    return render(request, 'home/stu-signup.html', {
        'user_form': user_form,
        'student_form': student_form,
        'teacher_form': teacher_form,
        'parent_form': parent_form,
        'role': role,
    })


# Login View
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST, request=request)
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
        form = CustomAuthenticationForm()

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



@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Error updating profile. Please check the form.")
    else:
        form = ProfileForm(instance=user)

    return render(request, 'profile.html', {'form': form, 'user': user})
