# payroll/models.py
from django.db import models
from employees.models import Employee

from django.db import models
from employees.models import Employee

class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.DateField()

    # Salary breakdown
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    pre_tax_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    post_tax_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    net_salary = models.DecimalField(max_digits=10, decimal_places=2)

    date_generated = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ['employee', 'month']

    def __str__(self):
        return f"{self.employee.name} - {self.month}"