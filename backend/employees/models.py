# employees/models.py
from django.db import models
from django.core.validators import RegexValidator

class Employee(models.Model):
    # Basic Identifier
    employee_id = models.CharField(
        max_length=20, 
        unique=True,
        help_text="Unique Employee ID (e.g., EMP-001)"
    )

    # Name
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)

    # Personal Info
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other'),
        ],
        blank=True,
        null=True
    )

    # Contact
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?\d{9,15}$')],
        blank=True,
        null=True
    )
    address = models.TextField(blank=True, null=True)

    # Employment Details
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True, null=True)
    date_joined = models.DateField()
    
    employment_status = models.CharField(
        max_length=20,
        choices=[
            ('Full-time', 'Full-time'),
            ('Part-time', 'Part-time'),
            ('Contractual', 'Contractual'),
        ],
        default='Full-time'
    )

    # Salary
    base_salary = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Monthly base salary"
    )

    # Bank Details (Optional)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=30, blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        middle = f" {self.middle_name}" if self.middle_name else ""
        return f"{self.first_name}{middle} {self.last_name}".strip()