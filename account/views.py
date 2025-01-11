from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm
from .forms import ContentForm, LoginForm
from django.utils.timezone import localtime
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from django.contrib import messages
from .forms import UserSignUpForm, StudentSignUpForm, TeacherSignUpForm, ParentSignUpForm
from .models import User, Student, Teacher, Parent, Timetable, StudentClass, Task

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
# Login View
def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)

                # Redirect based on the user's role
                if user.role == 'student':
                    return redirect('student_dashboard')  # Replace with your actual student dashboard URL
                elif user.role == 'teacher':
                    return redirect('teacher_dashboard')  # Replace with your actual teacher dashboard URL
                elif user.role == 'parent':
                    return redirect('parent_dashboard')  # Replace with your actual parent dashboard URL
                else:
                    return redirect('home')  # Fallback for unexpected roles
            else:
                form.add_error(None, 'Invalid email or password')
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
    # Determine the correct full name to display
    full_name = None
    if user.role == 'student':
        try:
            full_name = user.student.full_name
        except Student.DoesNotExist:
            full_name = "Student profile not found"
    elif user.role == 'teacher':
        try:
            full_name = user.teacher.full_name
        except Teacher.DoesNotExist:
            full_name = "Teacher profile not found"
    elif user.role == 'parent':
        try:
            full_name = user.parent.full_name
        except Parent.DoesNotExist:
            full_name = "Parent profile not found"
    else:
        full_name = user.fullname  # Fallback to the User model's fullname if no specific role

    # Handle form submission
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

    # Pass the form and full name to the template
    return render(request, 'profile.html', {'form': form, 'user': user, 'full_name': full_name})



def timetable_view(request):
    # Assuming you want to display the timetable for the logged-in student's class
    if request.user.is_authenticated and request.user.role == 'student':
        student = Student.objects.get(user=request.user)
        timetables = Timetable.objects.filter(student_class=student.student_class).order_by('day_of_week', 'start_time')
    else:
        # Default: Display all timetables
        timetables = Timetable.objects.all().order_by('day_of_week', 'start_time')
    
    return render(request, 'teachers-index.html', {'timetables': timetables})


def student_timetable_view(request):
    if request.user.is_authenticated and request.user.role == 'student':
        student = Student.objects.get(user=request.user)
        today = localtime().strftime('%A')  # Get the current day of the week (e.g., "Monday")
        
        # Filter timetables for the student's class and today's day
        timetables = Timetable.objects.filter(
            student_class=student.student_class, day_of_week=today
        ).order_by('start_time')
    else:
        timetables = None  # No timetables if the user isn't a student

    return render(request, 'student_timetable.html', {'timetables': timetables})


@login_required
def mark_task_complete(request, task_id):
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.completed = True
        task.save()
    except Task.DoesNotExist:
        pass
    return redirect('student_dashboard')


@login_required
def upload_content(request):
    user = request.user
    try:
        # Assuming a one-to-one relationship between user and teacher
        teacher_profile = user.teacher
        full_name = teacher_profile.full_name  # Retrieve full name from teacher profile
    except Teacher.DoesNotExist:
        teacher_profile = None
        full_name = "Teacher profile not found"

    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)  # Prevent saving to the database immediately
            content.teacher = teacher_profile  # Associate the content with the teacher
            content.save()
            return redirect('subject_content', subject_name=content.subject.name)  # Redirect to a success page or subject content
    else:
        form = ContentForm()
    
    return render(request, 'upload_content.html', {
        'form': form,
        'user': user,
        'full_name': full_name,
    })