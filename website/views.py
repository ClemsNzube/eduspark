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