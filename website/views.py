from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from account.models import User, Student, Teacher, Parent, Timetable, Task , Subject, Content
from django.utils.timezone import localtime



def home(request):
    return render(request, 'home/index.html')  

# # @login_required
# def student_dashboard(request):
#     return render(request, 'index.html')

# # @login_required
# def teacher_dashboard(request):
#     return render(request, 'teachers-index.html')

# # @login_required
# def parent_dashboard(request):
#     return render(request, 'parents-index.html')

# Student Dashboard
@login_required
def student_dashboard(request):
    user = request.user
    try:
        # Get the student's profile
        student_profile = user.student
        full_name = student_profile.full_name  # Get full name from student profile

        # Fetch today's timetable
        today = localtime().strftime('%A')  # Get the current day of the week (e.g., "Monday")
        timetables = Timetable.objects.filter(
            student_class=student_profile.student_class, day_of_week=today
        ).order_by('start_time')
    except Student.DoesNotExist:
        student_profile = None  # Handle case where the student profile does not exist
        full_name = "Student profile not found"  # Fallback if profile is missing
        timetables = None  # No timetables if student profile doesn't exist

    if request.method == 'POST':
        # Handle task creation
        if 'task' in request.POST:
            task_name = request.POST.get('task')
            if task_name:  # Ensure the task name is not empty
                Task.objects.create(name=task_name, user=user)
            return redirect('student_dashboard')

        # Handle marking tasks as completed
        if 'completed_tasks' in request.POST:
            completed_task_ids = request.POST.getlist('completed_tasks')
            Task.objects.filter(id__in=completed_task_ids, user=user).update(completed=True)
            return redirect('student_dashboard')

    # Fetch all tasks for the current user
    tasks = Task.objects.filter(user=user).order_by('-created_at')

    return render(request, 'index.html', {
        'user': user,
        'student_profile': student_profile,
        'full_name': full_name,  # Pass full_name to the template
        'timetables': timetables,  # Pass today's timetable to the template
        'tasks': tasks,  # Pass tasks to the template
    })

# Teacher Dashboard
@login_required
def teacher_dashboard(request):
    user = request.user
    try:
        teacher_profile = user.teacher  # Get the teacher profile linked to the logged-in user
        full_name = teacher_profile.full_name  # Get the full name from the teacher profile
        
        # Fetch the timetable where the teacher is assigned
        timetables = Timetable.objects.filter(teacher=teacher_profile).order_by('day_of_week', 'start_time')
    except Teacher.DoesNotExist:
        teacher_profile = None
        full_name = "Teacher profile not found"
        timetables = []  # No timetables for this case

    return render(request, 'teachers-index.html', {
        'user': user,
        'teacher_profile': teacher_profile,
        'full_name': full_name,  # Pass full_name to the template
        'timetables': timetables,  # Pass the timetables to the template
    })



# Parent Dashboard
@login_required
def parent_dashboard(request):
    user = request.user
    try:
        parent_profile = user.parent
        full_name = parent_profile.full_name  # Get full name from parent profile
    except Parent.DoesNotExist:
        parent_profile = None  # Handle case where the parent profile does not exist
        full_name = "Parent profile not found"  # Fallback if profile is missing

    return render(request, 'parents-index.html', {
        'user': user,
        'parent_profile': parent_profile,
        'full_name': full_name,  # Pass full_name to the template
    })



@login_required
def calendar(request):
    user = request.user
    full_name = None

    # Determine the full name based on the user's role
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
        full_name = user.fullname  # Fallback if no specific role exists

    return render(request, 'calendar.html', {'full_name': full_name})


@login_required
def grade(request):
    user = request.user
    full_name = None

    # Determine the full name based on the user's role
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
        full_name = user.fullname  # Fallback if no specific role exists

    return render(request, 'grade.html', {'full_name': full_name})


@login_required
def attendance(request):
    user = request.user
    full_name = None

    # Determine the full name based on the user's role
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
        full_name = user.fullname  # Fallback if no specific role exists

    return render(request, 'attendance.html', {'full_name': full_name})


@login_required
def report(request):
    user = request.user
    full_name = None

    # Determine the full name based on the user's role
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
        full_name = user.fullname  # Fallback if no specific role exists

    return render(request, 'invoice.html', {'full_name': full_name})




@login_required
def subject_content(request, subject_name):
    # Get the subject object based on the name passed in the URL
    try:
        subject = Subject.objects.get(name__iexact=subject_name)
    except Subject.DoesNotExist:
        return render(request, 'subject_not_found.html')  # Show an error page if subject not found

    # Get the content for today's date
    today = date.today()
    contents = Content.objects.filter(subject=subject, date_uploaded=today)

    # Get the logged-in user
    user = request.user

    # Determine if the user is a teacher or a student
    is_teacher = False
    try:
        # Check if the user has a teacher profile
        teacher_profile = user.teacher  # Assumes a one-to-one relationship between user and teacher
        profile = teacher_profile  # Use the teacher profile
        full_name = teacher_profile.full_name
        profile_type = "teacher"
        is_teacher = True
    except Teacher.DoesNotExist:
        teacher_profile = None

        # Check if the user has a student profile
        try:
            student_profile = user.student  # Assumes a one-to-one relationship between user and student
            profile = student_profile  # Use the student profile
            full_name = student_profile.full_name
            profile_type = "student"
        except Student.DoesNotExist:
            profile = None
            full_name = "Profile not found"
            profile_type = "unknown"

    return render(request, 'subject_content.html', {
        'subject': subject,
        'contents': contents,
        'today': today,
        'user': user,
        'full_name': full_name,
        'profile': profile,
        'profile_type': profile_type,
        'is_teacher': is_teacher,  # Pass this to the template
    })