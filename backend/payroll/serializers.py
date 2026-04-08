# payroll/serializers.py
from rest_framework import serializers
from decimal import Decimal
from datetime import date, timedelta
from .models import Payroll
from employees.models import Employee
from attendance.models import Attendance
from employees.serializers import EmployeeSerializer


class PayrollSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )

    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'employee_id',
            'period_start', 'period_end',
            'gross_salary',
            'overtime_pay',
            'holiday_pay',              
            'pre_tax_deductions',
            'tax',
            'post_tax_deductions',
            'net_salary',
            'date_generated',
        ]
        read_only_fields = [
            'gross_salary', 'overtime_pay', 'holiday_pay',
            'pre_tax_deductions', 'tax', 'post_tax_deductions',
            'net_salary', 'date_generated'
        ]

    def validate(self, data):
        if 'period_start' not in data or 'period_end' not in data:
            today = date.today()
            if today.day <= 15:
                data['period_start'] = today.replace(day=1)
                data['period_end'] = today.replace(day=15)
            else:
                data['period_start'] = today.replace(day=16)
                next_month = today.replace(day=28) + timedelta(days=4)
                last_day = next_month.replace(day=1) - timedelta(days=1)
                data['period_end'] = last_day
        return data

    def create(self, validated_data):
        employee = validated_data['employee']
        period_start = validated_data['period_start']
        period_end = validated_data['period_end']

        if Payroll.objects.filter(employee=employee, period_start=period_start, period_end=period_end).exists():
            raise serializers.ValidationError("Payroll for this period already exists.")

        try:
            attendance = Attendance.objects.get(
                employee=employee,
                period_start=period_start,
                period_end=period_end
            )
        except Attendance.DoesNotExist:
            raise serializers.ValidationError("Attendance record not found for this period.")

        monthly_base = employee.base_salary
        biweekly_base = monthly_base / Decimal('2')
        daily_rate = monthly_base / Decimal('22')
        hourly_rate = daily_rate / Decimal('8')

        # Overtime Pay (1.5x)
        overtime_pay = (attendance.overtime_hours * hourly_rate * Decimal('1.5')).quantize(Decimal('0.01'))

        # Holiday Pay (2x daily rate - common practice)
        holiday_pay = (Decimal(attendance.holiday_worked) * daily_rate * Decimal('2')).quantize(Decimal('0.01'))

        # Final Gross
        final_gross = (biweekly_base + overtime_pay + holiday_pay).quantize(Decimal('0.01'))

        pre_tax_deductions = (daily_rate * Decimal(attendance.absences)).quantize(Decimal('0.01'))

        monthly_tax = self.calculate_monthly_tax(monthly_base)
        tax = (monthly_tax / Decimal('2')).quantize(Decimal('0.01'))

        post_tax_deductions = Decimal('250')

        net_salary = (final_gross - pre_tax_deductions - tax - post_tax_deductions).quantize(Decimal('0.01'))

        payroll = Payroll.objects.create(
            employee=employee,
            period_start=period_start,
            period_end=period_end,
            gross_salary=final_gross,
            overtime_pay=overtime_pay,
            holiday_pay=holiday_pay,
            pre_tax_deductions=pre_tax_deductions,
            tax=tax,
            post_tax_deductions=post_tax_deductions,
            net_salary=net_salary,
        )

        return payroll

    def calculate_monthly_tax(self, gross: Decimal) -> Decimal:
        if gross <= 20000:
            return gross * Decimal('0.05')
        elif gross <= 40000:
            return gross * Decimal('0.10')
        else:
            return gross * Decimal('0.15')