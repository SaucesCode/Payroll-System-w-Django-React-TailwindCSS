# attendance/models.py
from django.db import models
from employees.models import Employee

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="attendances")
    days_worked = models.IntegerField()
    absences = models.IntegerField()
    month = models.DateField()  # track which month this attendance is for

    def __str__(self):
        return f"{self.employee.name} - {self.month.strftime('%B %Y')}"