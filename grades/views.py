from django.shortcuts import render, redirect
from account.models import Student, Submission, Subject, Teacher
from django.shortcuts import get_object_or_404, render
from .models import Grade
from django.db.models import F
from django.contrib.auth.decorators import login_required


@login_required
def student_grades(request):
    """
    View for students to see their grades for each subject.
    """
    # Get the logged-in user's student profile
    try:
        student_profile = request.user.student  # Assuming a one-to-one relationship between user and student
        full_name = student_profile.full_name
        profile_type = "student"
    except Student.DoesNotExist:
        student_profile = None
        full_name = "Student profile not found"
        profile_type = "unknown"

    # Get all grades for the student
    if student_profile:
        grades = Grade.objects.filter(student=student_profile).select_related('subject')  # Fetch grades for the student
    else:
        grades = []

    # Calculate the total score percentage
    total_score = 0
    if grades.exists():
        total_score = sum(grade.score for grade in grades) / grades.count()

    return render(request, 'student_grades.html', {
        'grades': grades,
        'student': student_profile,
        'total_score': total_score,  # Pass total score to template
        'full_name': full_name,
        'profile_type': profile_type,
    })




@login_required
def teacher_grades(request):
    """
    View for teachers to see grades of all students in their assigned class.
    """
    teacher = get_object_or_404(Teacher, user=request.user)  # Get the logged-in teacher's profile

    if not teacher.assigned_class:
        return render(request, 'teacher_grades.html', {
            'error': 'No class assigned to this teacher.'
        })

    # Fetch all students in the assigned class
    students = Student.objects.filter(student_class=teacher.assigned_class).select_related('student_class')
    grades = Grade.objects.filter(student__in=students).select_related('student', 'subject')  # Get grades for those students

    return render(request, 'teacher_grades.html', {
        'grades': grades,
        'students': students,
        'teacher': teacher,
    })