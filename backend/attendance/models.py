# attendance/models.py
from django.db import models
from employees.models import Employee
from datetime import timedelta

class Holiday(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField(unique=True)
    is_recurring = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.name} ({self.date})"


class Attendance(models.Model):
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name="attendances"
    )
    
    days_worked = models.PositiveIntegerField(default=0)
    absences = models.PositiveIntegerField(default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # New: Holiday Work Tracking
    holiday_worked = models.PositiveIntegerField(default=0, help_text="Number of holidays worked during this period")
    
    period_start = models.DateField()
    period_end = models.DateField()

    class Meta:
        unique_together = ['employee', 'period_start', 'period_end']
        ordering = ['-period_start', '-period_end']

    def __str__(self):
        return f"{self.employee.full_name} ({self.period_start} to {self.period_end})"

    def save(self, *args, **kwargs):
        if self.period_start and self.period_end:
            total_working_days = 0
            current = self.period_start
            while current <= self.period_end:
                if current.weekday() >= 5:  # weekend
                    current += timedelta(days=1)
                    continue
                if Holiday.objects.filter(date=current).exists():
                    current += timedelta(days=1)
                    continue
                total_working_days += 1
                current += timedelta(days=1)

            self.days_worked = max(0, total_working_days - self.absences)

        super().save(*args, **kwargs)