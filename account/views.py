from datetime import timedelta, timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from io import BytesIO
from django.http import HttpResponse
from xhtml2pdf import pisa
from decimal import Decimal
from django.contrib.auth.forms import PasswordResetForm
from .forms import ContentForm, LoginForm
from django.utils.timezone import localtime
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from django.contrib import messages
from .forms import UserSignUpForm, StudentSignUpForm, TeacherSignUpForm, ParentSignUpForm
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

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
                    parent.save()  # Save the Parent instance first to get the ID
                    
                    # Save the children (Many-to-Many relationship)
                    children = parent_form.cleaned_data.get('children')  # Get selected children
                    parent.children.set(children)  # Use set() to add the relationships

                    parent.save()  # Save again after setting the Many-to-Many field


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

            # Ensure subject is always assigned for assignments
            if content.content_type == 'assignment':
                if not content.subject:
                    # Raise an error or handle the case where no subject is selected
                    form.add_error('subject', 'A subject must be assigned to an assignment.')
                    return render(request, 'upload_content.html', {'form': form, 'user': user, 'full_name': full_name})

            content.save()
            # Redirect based on content type
            if content.content_type == 'assignment':
                return redirect('upcoming_homework')  # Redirect to the upcoming homework page
            else:
                return redirect('subject_content', subject_name=content.subject.name)

    else:
        form = ContentForm()

    return render(request, 'upload_content.html', {
        'form': form,
        'user': user,
        'full_name': full_name,
    })


@login_required
def submit_answer(request, content_id):
    # Get the assignment content
    content = get_object_or_404(Content, id=content_id, content_type='assignment')
    
    if request.method == 'POST':
        student = Student.objects.get(user=request.user)  # Get the Student instance associated with the logged-in user

        # Get the answer from the form submission
        answer = request.POST.get('answer')

        # Create a Submission object to store the student's answer
        submission = Submission.objects.create(
            content=content,
            student=student,
            subject=content.subject,  # Set the subject from the content
            answer=answer
        )

        # Check if the assignment was submitted within 24 hours
        if timezone.now() - content.date_uploaded <= timedelta(hours=24):
            # Mark the attendance as attended and award 5 points
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                subject=content.subject,
                content=content  # Associate attendance with the specific content (assignment)
            )

            attendance.attended = True
            attendance.attendance_points = 5  # Add 5 points for attendance
            attendance.save()

        else:
            # Mark the attendance as absent if the submission is late (more than 24 hours)
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                subject=content.subject,
                content=content
            )

            attendance.attended = False
            attendance.attendance_points = 0  # No points for late submission
            attendance.save()

        return redirect('completed_assignments')  # Redirect to the "Completed Assignments" page for students

    return redirect('upcoming_homework')  # Default redirect if no form submission


@login_required
def view_attendance(request, subject_id=None):
    user = request.user
    
    # Case for student viewing their attendance
    if hasattr(user, 'student'):  # Check if the user has a student profile
        student_profile = user.student
        attendances = Attendance.objects.filter(student=student_profile).select_related('subject', 'content')
        return render(request, 'attendance_list.html', {
            'attendances': attendances,
            'student': student_profile,
        })
    
    # Case for teacher viewing student attendance
    elif hasattr(user, 'teacher'):  # Check if the user has a teacher profile
        teacher_profile = user.teacher
        
        if not teacher_profile.assigned_class:
            return render(request, 'attendance_list.html', {
                'error': 'This teacher does not have an assigned class.'
            })

        # Fetch students in the teacher's assigned class
        students_in_class = Student.objects.filter(student_class=teacher_profile.assigned_class).select_related('student_class')
        
        # If subject_id is provided, fetch attendance for that specific subject
        if subject_id:
            subject = get_object_or_404(Subject, id=subject_id)
            if teacher_profile not in subject.teachers.all():
                return redirect('unauthorized')  # Redirect if teacher isn't assigned to the subject
            
            # Get attendance records for the students in the assigned class for the specific subject
            attendances = Attendance.objects.filter(subject=subject, student__in=students_in_class).select_related('student')
        else:
            # If no subject_id, fetch all attendance records for the teacher's assigned class across all subjects
            attendances = Attendance.objects.filter(student__in=students_in_class).select_related('student', 'subject')

        return render(request, 'attendance_list.html', {
            'attendances': attendances,
            'teacher': teacher_profile,
            'students_in_class': students_in_class,  # Pass the students to the template
        })




@login_required
def student_attendance(request):
    """
    View for students to see their attendance for each subject.
    """
    user = request.user

    # Check if the user has a student profile (assuming a one-to-one relationship between user and student)
    try:
        student_profile = user.student  # Assuming the User model has a related Student profile
        full_name = student_profile.full_name
        profile_type = "student"
    except Student.DoesNotExist:
        student_profile = None
        full_name = "Student profile not found"
        profile_type = "unknown"

    # Fetch all attendance records for the student, ordered by subject and assignment date
    if student_profile:
        attendance_records = Attendance.objects.filter(student=student_profile).select_related('subject', 'content').order_by('-date')
    else:
        attendance_records = []

    return render(request, 'student_attendance.html', {
        'attendance_records': attendance_records,
        'full_name': full_name,
        'profile_type': profile_type,
    })



@login_required
def calendar_view(request):
    events = Event.objects.all().order_by('-start_time')

    # Filter events based on user type (teacher or student)
    if hasattr(request.user, 'teacher'):
        events = events.filter(teacher=request.user)
    elif hasattr(request.user, 'student'):
        events = events.filter(is_general=True)  # Students can only see general events

    return render(request, 'calendar.html', {'events': events})

@login_required
def create_event(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        is_general = request.POST.get('is_general', False)

        # Create a new event
        event = Event.objects.create(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            is_general=is_general,
            teacher=request.user if hasattr(request.user, 'teacher') else None,
        )

        return JsonResponse({'status': 'success', 'event_id': event.id})
    

import os

@login_required
def materials_view(request):
    user = request.user

    # Initialize variables for profile details
    full_name = "Profile not found"
    profile_type = "unknown"

    # Retrieve the student's profile, if available
    try:
        student_profile = user.student  # Assuming a one-to-one relationship between User and Student
        full_name = student_profile.full_name
        profile_type = "student"
    except Student.DoesNotExist:
        student_profile = None

    # Retrieve the teacher's profile, if available
    try:
        teacher_profile = user.teacher  # Assuming a one-to-one relationship between User and Teacher
        full_name = teacher_profile.full_name
        profile_type = "teacher"
    except Teacher.DoesNotExist:
        teacher_profile = None

    # Handle material upload (only teachers are allowed)
    if request.method == 'POST':
        if profile_type != "teacher":
            messages.error(request, 'You are not authorized to upload materials.')
            return redirect('materials')

        title = request.POST.get('title')
        description = request.POST.get('description')
        file = request.FILES.get('file')
        if title and file:
            material = Material.objects.create(
                title=title,
                description=description,
                file=file,
                uploaded_by=user
            )
            messages.success(request, 'Material uploaded successfully!')
        else:
            messages.error(request, 'All fields are required.')
        return redirect('materials')

    # Add file type to materials
    materials = Material.objects.all()
    for material in materials:
        _, ext = os.path.splitext(material.file.name)  # Get file extension
        ext = ext.lower()
        if ext == '.pdf':
            material.file_type = 'PDF Document'
        elif ext == '.mp4':
            material.file_type = 'Video'
        elif ext == '.mp3':
            material.file_type = 'Audio'
        elif ext in ['.doc', '.docx']:
            material.file_type = 'Word Document'
        elif ext in ['.ppt', '.pptx']:
            material.file_type = 'Presentation'
        else:
            material.file_type = 'Other'

    return render(request, 'materials.html', {
        'materials': materials,
        'full_name': full_name,
        'profile_type': profile_type,
    })



@login_required
def generate_report(request):
    """
    View for generating a report document for the logged-in student.
    """
    user = request.user  # Get the logged-in user
    
    try:
        student = user.student  # Assuming the User model has a related Student profile
        school = student.school  # Assuming the Student model has a 'school' field
    except Student.DoesNotExist:
        return HttpResponse('Student profile not found', status=404)
    
    # Get grades for the student
    grades = Grade.objects.filter(student=student).select_related('subject')
    attendance = Attendance.objects.filter(student=student).select_related('subject')
    
    # Calculate total grades and attendance
    total_grades = sum(grade.score for grade in grades)
    total_attendance_points = sum(attendance.attendance_points for attendance in attendance)
    
    # Calculate the averages
    total_subjects = grades.count()
    total_attendance_subjects = attendance.count()

    if total_subjects > 0:
        average_grade = Decimal(total_grades) / total_subjects  # Convert to Decimal
    else:
        average_grade = Decimal(0)  # Use Decimal for consistency

    if total_attendance_subjects > 0:
        average_attendance = Decimal(total_attendance_points) / total_attendance_subjects  # Convert to Decimal
    else:
        average_attendance = Decimal(0)  # Use Decimal for consistency

    combined_average = (average_grade + average_attendance) / 2
    
    # Determine overall grade based on the combined average
    if combined_average >= Decimal(75):
        overall_grade = 'Distinction'
    elif combined_average >= Decimal(60):
        overall_grade = 'Credit'
    elif combined_average >= Decimal(50):
        overall_grade = 'Merit'
    elif combined_average >= Decimal(40):
        overall_grade = 'Pass'
    else:
        overall_grade = 'Failure'
    
    # Get student report for the student
    report, created = StudentReport.objects.get_or_create(
        student=student, school=school, 
        defaults={'total_average': combined_average, 'overall_grade': overall_grade}
    )
    
    # Prepare context for rendering the template
    context = {
        'student': student,
        'school': school,
        'grades': grades,
        'attendance': attendance,
        'total_grades': total_grades,
        'total_attendance_points': total_attendance_points,
        'average_grade': average_grade,
        'average_attendance': average_attendance,
        'combined_average': combined_average,
        'overall_grade': overall_grade,
    }

    # Render the template into HTML
    html = render_to_string('report.html', context)
    
    # Convert the HTML to a PDF document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student.full_name}_report.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    
    return response

@login_required
def parent_attendance(request):
    """
    View for parents to see their child's attendance for each subject.
    """
    user = request.user
    
    # Check if the user has a parent profile (assuming a one-to-one relationship between user and parent)
    try:
        parent_profile = user.parent  # Assuming the User model has a related Parent profile
        children_profiles = parent_profile.children.all()  # Get all children related to the parent
        profile_type = "parent"
        full_name = parent_profile.full_name  # Set full_name to the parent's full name
    except Parent.DoesNotExist:
        parent_profile = None
        children_profiles = []
        full_name = "Parent profile or children not found"
        profile_type = "unknown"

    # Check if we have any children profiles
    if children_profiles:
        # You can either select a specific child for the parent to view or iterate through all
        student_profile = children_profiles.first()  # Just take the first child (you can change this logic)
        
        # Fetch all attendance records for the first child, ordered by subject and assignment date
        attendance_records = Attendance.objects.filter(student=student_profile).select_related('subject', 'content').order_by('-timestamp')
    else:
        attendance_records = []
        student_profile = None  # No student profile if there are no children
    
    return render(request, 'parent_attendance.html', {
        'attendance_records': attendance_records,
        'full_name': full_name,  # Parent's full name is now passed to the template
        'profile_type': profile_type,
        'student': student_profile,
    })


@login_required
def parent_report(request):
    """
    View for parents to access their child's report.
    Assumes each parent has only one child.
    """
    user = request.user
    try:
        # Get the parent profile linked to the logged-in user
        parent_profile = user.parent
        full_name = parent_profile.full_name  # Assuming Parent model has a full_name field

        # Fetch the first (and only) child linked to the parent
        child = parent_profile.children.first()
        if not child:
            raise ValueError("No child linked to this parent profile.")

        # Fetch or create the report for the child
        report = StudentReport.objects.get_or_create(student=child)[0]

        # Pass necessary data to the template
        context = {
            'full_name': full_name,
            'report': report,
        }
        return render(request, 'parent_reports.html', context)

    except (Parent.DoesNotExist, ValueError) as e:
        # Handle cases where the parent profile or child is not found
        return render(request, 'error.html', {
            'message': str(e) or "Parent profile or child not found."
        })
