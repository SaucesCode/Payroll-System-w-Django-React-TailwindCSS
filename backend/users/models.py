# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('payroll_officer', 'Payroll Officer'),
        ('employee', 'Employee'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='employee'
    )
    
    # Link to Employee profile (for Employee role)
    employee_profile = models.OneToOneField(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_account'
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_payroll_officer(self):
        return self.role in ['admin', 'payroll_officer']