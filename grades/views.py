from django.shortcuts import render
from account.models import Submission, Subject
from .models import Grade
from django.db.models import F
from django.contrib.auth.decorators import login_required


@login_required
def student_performance(request):
    student = request.user.student  # Assuming the logged-in user is a student
    submissions = Submission.objects.filter(student=student)
    grades = Grade.objects.filter(student=student)

    # Initialize subject grades with A (100)
    subject_grades = {grade.subject.name: 100 for grade in grades}

    # Process the submissions and update grades based on status
    for submission in submissions:
        subject_name = submission.content.subject.name  # Get the subject for the submission
        if submission.status == 'correct':
            # Increase the grade by 5 points, but not exceeding 100
            subject_grades[subject_name] = min(subject_grades[subject_name] + 5, 100)
        elif submission.status == 'incorrect':
            # Decrease the grade by 5 points for each incorrect submission
            subject_grades[subject_name] = max(subject_grades[subject_name] - 5, 0)

    # Calculate the overall grade based on the average score of all subjects
    total_score = sum(subject_grades.values())
    overall_grade = calculate_overall_grade(total_score / len(subject_grades))

    # Prepare letter grades for each subject
    letter_grades = {
        subject: get_letter_grade(score) 
        for subject, score in subject_grades.items()
    }

    # Prepare data for the chart
    chart_data = {
        'subjects': list(subject_grades.keys()),
        'scores': list(subject_grades.values()),
    }

    # Pass everything to the template context
    return render(request, 'student_performance.html', {
        'subject_grades': subject_grades,
        'overall_grade': overall_grade,
        'letter_grades': letter_grades,
        'chart_data': chart_data,
    })

# Helper functions
def calculate_overall_grade(average_score):
    if average_score >= 85:
        return 'A'
    elif average_score >= 70:
        return 'B'
    elif average_score >= 60:
        return 'C'
    elif average_score >= 50:
        return 'D'
    elif average_score >= 45:
        return 'E'
    else:
        return 'F'

def get_letter_grade(score):
    if score >= 85:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 60:
        return 'C'
    elif score >= 50:
        return 'D'
    elif score >= 45:
        return 'E'
    else:
        return 'F'
