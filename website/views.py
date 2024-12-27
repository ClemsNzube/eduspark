from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'home/index.html')  

# @login_required
def student_dashboard(request):
    return render(request, 'index.html')

# @login_required
def teacher_dashboard(request):
    return render(request, 'teachers-index.html')

# @login_required
def parent_dashboard(request):
    return render(request, 'parents-index.html')

 
def calendar(request):
    return render(request, 'calendar.html')

def grade(request):
    return render(request, 'grade.html')

def attendance(request):
    return render(request, 'attendance.html')

def report(request):
    return render(request, 'invoice.html')
