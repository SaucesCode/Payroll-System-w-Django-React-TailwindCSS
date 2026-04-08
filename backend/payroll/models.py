# payroll/models.py
from django.db import models
from employees.models import Employee

class Payroll(models.Model):
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name="payrolls"
    )
    
    period_start = models.DateField()
    period_end = models.DateField()
    
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)
    overtime_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    holiday_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)   # ← New
    
    pre_tax_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    post_tax_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)

    date_generated = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['employee', 'period_start', 'period_end']
        ordering = ['-period_start', '-period_end']

    def __str__(self):
        return f"{self.employee.full_name} - {self.period_start} to {self.period_end}"