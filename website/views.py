from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from account.models import User, Student, Teacher, Parent



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
        student_profile = user.student
        full_name = student_profile.full_name  # Get full name from student profile
    except Student.DoesNotExist:
        student_profile = None  # Handle case where the student profile does not exist
        full_name = "Student profile not found"  # Fallback if profile is missing

    return render(request, 'index.html', {
        'user': user,
        'student_profile': student_profile,
        'full_name': full_name,  # Pass full_name to the template
    })


# Teacher Dashboard
@login_required
def teacher_dashboard(request):
    user = request.user
    try:
        teacher_profile = user.teacher
        full_name = teacher_profile.full_name  # Get full name from teacher profile
    except Teacher.DoesNotExist:
        teacher_profile = None  # Handle case where the teacher profile does not exist
        full_name = "Teacher profile not found"  # Fallback if profile is missing

    return render(request, 'teachers-index.html', {
        'user': user,
        'teacher_profile': teacher_profile,
        'full_name': full_name,  # Pass full_name to the template
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

