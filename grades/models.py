from django.db import models

# Create your models here.

class Grade(models.Model):
    student = models.ForeignKey('account.Student', on_delete=models.CASCADE, related_name="grades")
    subject = models.ForeignKey('account.Subject', on_delete=models.CASCADE, related_name="grades", null=True, blank=True)
    submission = models.ForeignKey('account.Submission', on_delete=models.CASCADE, related_name="grades", null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)  # Default to 100
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.full_name}'s grade in : {self.score}"

    @property
    def letter_grade(self):
        """Returns the letter grade based on the numeric score."""
        if self.score >= 75:
            return "A"
        elif self.score >= 60:
            return "B"
        elif self.score >= 50:
            return "C"
        elif self.score >= 40:
            return "D"
        else:
            return "F"



class TeacherFeedback(models.Model):
    student = models.ForeignKey('account.Student', on_delete=models.CASCADE)
    feedback = models.TextField()
    date_given = models.DateField()

    def __str__(self):
        return f"Feedback for {self.student.full_name}"