from django.shortcuts import render, redirect
from account.models import Parent, Student, Submission, Subject, Teacher
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


@login_required
def parent_grades(request):
    """
    View for parents to see their child's grades for each subject.
    """
    # Get the logged-in user's parent profile
    try:
        parent_profile = request.user.parent  # Assuming a one-to-one relationship between user and parent
        full_name = parent_profile.full_name
        profile_type = "parent"
    except Parent.DoesNotExist:
        parent_profile = None
        full_name = "Parent profile not found"
        profile_type = "unknown"

    # Get the children linked to the parent (Many-to-many relationship)
    if parent_profile:
        children = parent_profile.children.all()  # All students (children) linked to this parent
    else:
        children = []

    # Get grades for each child
    grades_data = []
    for child in children:
        grades = Grade.objects.filter(student=child).select_related('subject')  # Fetch grades for the student
        total_score = 0
        if grades.exists():
            total_score = sum(grade.score for grade in grades) / grades.count()
        grades_data.append({
            'student': child,
            'grades': grades,
            'total_score': total_score
        })

    return render(request, 'parent_grades.html', {
        'grades_data': grades_data,
        'parent': parent_profile,
        'full_name': full_name,
        'profile_type': profile_type,
    })