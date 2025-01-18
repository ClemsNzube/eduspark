from django.db import models
from account.models import Student, Subject

# Create your models here.

class Grade(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F')])

    def __str__(self):
        return f"{self.subject.name} Grade for {self.student.full_name}"

class TeacherFeedback(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    date_given = models.DateField()

    def __str__(self):
        return f"Feedback for {self.student.full_name}"