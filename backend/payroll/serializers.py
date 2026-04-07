from rest_framework import serializers
from .models import Payroll
from employees.models import Employee
from attendance.models import Attendance
from employees.serializers import EmployeeSerializer
from decimal import Decimal

class PayrollSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )

    class Meta:
        model = Payroll
        fields = '__all__'
        read_only_fields = [
            'gross_salary',
            'pre_tax_deductions',
            'tax',
            'post_tax_deductions',
            'net_salary',
            'date_generated'
        ]

    def create(self, validated_data):
        employee = validated_data['employee']
        month = validated_data['month']

        attendance = Attendance.objects.get(employee=employee, month=month)

        # 1. Gross salary
        gross_salary = employee.base_salary

        # 2. Absence deduction
        daily_rate = employee.base_salary / Decimal('22')
        absence_deduction = daily_rate * Decimal(attendance.absences)
        
        pre_tax = absence_deduction

        # 3. Tax calculation
        if gross_salary <= 20000:
            tax = gross_salary * Decimal('0.05')
        elif gross_salary <= 40000:
            tax = gross_salary * Decimal('0.10')
        else:
            tax = gross_salary * Decimal('0.15')

        # 4. Post-tax deduction
        post_tax = 500

        # 5. Net salary
        net_salary = gross_salary - pre_tax - tax - post_tax

        payroll = Payroll.objects.create(
            employee=employee,
            month=month,
            gross_salary=gross_salary,
            pre_tax_deductions=pre_tax,
            tax=tax,
            post_tax_deductions=post_tax,
            net_salary=net_salary
        )

        return payroll