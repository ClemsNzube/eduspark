from datetime import date
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from account.models import Event, Submission, User, Student, Teacher, Parent, Timetable, Task , Subject, Content
from django.utils.timezone import localtime
from account.forms import SubmissionFeedbackForm
from grades.models import Grade



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



@login_required
def parent_dashboard(request):
    user = request.user

    try:
        # Get the parent's profile
        parent_profile = user.parent
        full_name = parent_profile.full_name  # Get the parent's full name

        # Fetch all children associated with the parent
        children = parent_profile.children.all()

        # Fetch grades for each child
        children_grades = {
            child: Grade.objects.filter(student=child).order_by('-last_updated')
            for child in children
        }

        # Fetch upcoming events visible to children (general or specific to their teachers)
        upcoming_events = Event.objects.filter(is_general=True).order_by('start_time')

        # Fetch today's timetable for each child
        today = localtime().strftime('%A')  # Get the current day of the week (e.g., "Monday")
        children_timetables = {
            child: Timetable.objects.filter(
                student_class=child.student_class, day_of_week=today
            ).order_by('start_time')
            for child in children
        }

    except Parent.DoesNotExist:
        parent_profile = None
        full_name = "Parent profile not found"
        children = []
        children_grades = {}
        upcoming_events = None
        children_timetables = {}

    # Render the parent dashboard template
    return render(request, 'parents-index.html', {
        'parent_profile': parent_profile,
        'full_name': full_name,  # Pass parent's full name to the template
        'children': children,  # Pass children to the template
        'children_grades': children_grades,  # Pass grades for each child
        'upcoming_events': upcoming_events,  # Pass upcoming events to the template
        'children_timetables': children_timetables,  # Pass today's timetables for each child
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


# @login_required
# def grade(request):
#     user = request.user
#     full_name = None

#     # Determine the full name based on the user's role
#     if user.role == 'student':
#         try:
#             full_name = user.student.full_name
#         except Student.DoesNotExist:
#             full_name = "Student profile not found"
#     elif user.role == 'teacher':
#         try:
#             full_name = user.teacher.full_name
#         except Teacher.DoesNotExist:
#             full_name = "Teacher profile not found"
#     elif user.role == 'parent':
#         try:
#             full_name = user.parent.full_name
#         except Parent.DoesNotExist:
#             full_name = "Parent profile not found"
#     else:
#         full_name = user.fullname  # Fallback if no specific role exists

#     return render(request, 'grade.html', {'full_name': full_name})


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
    # contents = Content.objects.filter(subject=subject, date_uploaded=today)
    contents = Content.objects.filter(subject=subject, content_type__in=['lecture', 'note'], date_uploaded=today)

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


@login_required
def upcoming_homework(request):
    # Get the logged-in user
    user = request.user

    # Check if the user is a teacher or a student
    is_teacher = False
    profile = None
    full_name = "Profile not found"
    profile_type = "unknown"

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
            student_profile = None

    # Get today's date
    today = date.today()

    # Filter content for 'assignment' type, regardless of subject, for today
    assignments = Content.objects.filter(
        content_type='assignment',
        date_uploaded=today
    ).order_by('date_uploaded')

    # Render the template with the filtered assignments
    return render(request, 'upcoming_homework.html', {
        'assignments': assignments,
        'today': today,
        'user': user,
        'full_name': full_name,
        'profile': profile,
        'profile_type': profile_type,
        'is_teacher': is_teacher,  # Pass this to the template
    })



# @login_required
# def submit_answer(request, assignment_id):
#     # Get the assignment based on the ID
#     assignment = Content.objects.get(id=assignment_id)

#     if request.method == 'POST':
#         # Get the answer from the form
#         answer = request.POST.get('answer')
        
#         # Save the answer (you can associate this with a student model if necessary)
#         # For example, if you have a model for storing student answers:
#         # Answer.objects.create(student=request.user.student, assignment=assignment, answer_text=answer)

#         # You can store the answer here or perform any necessary logic

#         # messages.success(request, 'Your answer has been submitted successfully!')
#         return redirect('upcoming_homework')
    

@login_required
def submitted_assignments(request):
    if not hasattr(request.user, 'teacher'):
        return redirect('home')  # Ensure only teachers can access this page

    # Get all submissions grouped by the assignment
    submissions = Submission.objects.select_related('content', 'student', 'subject').all()

    # Group submissions by assignment
    grouped_submissions = {}
    for submission in submissions:
        if submission.content not in grouped_submissions:
            grouped_submissions[submission.content] = []
        grouped_submissions[submission.content].append(submission)

    # Handle feedback form submission
    if request.method == 'POST':
        for submission in submissions:
            feedback = request.POST.get(f'feedback_{submission.id}')
            status = request.POST.get(f'status_{submission.id}')
            
            if feedback or status:
                # Update the submission with new feedback and status
                previous_status = submission.status
                submission.feedback = feedback
                submission.status = status
                submission.save()

                # Update the student's grade for the subject
                grade, created = Grade.objects.get_or_create(
                    student=submission.student,
                    subject=submission.subject
                )

                # Update grade score based on the new status
                if status == 'correct' and previous_status != 'correct':
                    grade.score = min(100, grade.score + 5)
                elif status == 'incorrect' and previous_status != 'incorrect':
                    grade.score -= 10
                elif status == 'pending' and previous_status == 'correct':
                    grade.score -= 5

                # Ensure the grade score stays within bounds
                grade.score = max(0, grade.score)
                grade.save()

        return redirect('submitted_assignments')  # Redirect to the same page to show updates

    return render(request, 'submitted_assignments.html', {
        'grouped_submissions': grouped_submissions,
    })


@login_required
def completed_assignments(request):
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

    # Get all completed assignments for the student
    if student_profile:
        completed_submissions = Submission.objects.filter(student=student_profile).order_by('-date_submitted')
    else:
        completed_submissions = []

    return render(request, 'completed_assignments.html', {
        'completed_submissions': completed_submissions,
        'full_name': full_name,
        'profile_type': profile_type,
    })

