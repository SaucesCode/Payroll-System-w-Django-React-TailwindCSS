# payroll/serializers.py
from rest_framework import serializers
from decimal import Decimal
from datetime import date, timedelta
from .models import Payroll
from employees.models import Employee
from attendance.models import Attendance
from employees.serializers import EmployeeSerializer


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
    
    # Fixed: Truly optional for "All Employees" generation
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'employee_id',
            'period_start', 'period_end',
            'gross_salary', 'overtime_pay', 'holiday_pay',
            'pre_tax_deductions', 'tax', 'post_tax_deductions', 'net_salary',
            'date_generated',
        ]
        read_only_fields = [
            'gross_salary', 'overtime_pay', 'holiday_pay',
            'pre_tax_deductions', 'tax', 'post_tax_deductions',
            'net_salary', 'date_generated'
        ]

    def validate(self, data):
        """Auto-fill current period if not provided"""
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
        period_start = validated_data['period_start']
        period_end = validated_data['period_end']
        employee = validated_data.get('employee')  # This will be None for "All Employees"

        created = []

        if employee:  
            # Single employee
            employees_list = [employee]
        else:  
            # All active employees
            employees_list = Employee.objects.filter(is_active=True)

        for emp in employees_list:
            try:
                attendance = Attendance.objects.get(
                    employee=emp,
                    period_start=period_start,
                    period_end=period_end
                )
                payroll = self._create_single_payroll(emp, attendance, period_start, period_end)
                if payroll:
                    created.append(payroll)
            except Attendance.DoesNotExist:
                continue

        if not created:
            raise serializers.ValidationError(
                "No attendance records found for the selected period. "
                "Please create attendance first."
            )

        return created[0]   # Return first created record for DRF response

    def _create_single_payroll(self, employee, attendance, period_start, period_end):
        if Payroll.objects.filter(
            employee=employee, 
            period_start=period_start, 
            period_end=period_end
        ).exists():
            return None

        monthly_base = employee.base_salary
        biweekly_base = monthly_base / Decimal('2')
        daily_rate = monthly_base / Decimal('22')
        hourly_rate = daily_rate / Decimal('8')

        overtime_pay = (attendance.overtime_hours * hourly_rate * Decimal('1.5')).quantize(Decimal('0.01'))
        holiday_pay = (Decimal(attendance.holiday_worked) * daily_rate * Decimal('2')).quantize(Decimal('0.01'))

        final_gross = (biweekly_base + overtime_pay + holiday_pay).quantize(Decimal('0.01'))
        pre_tax_deductions = (daily_rate * Decimal(attendance.absences)).quantize(Decimal('0.01'))
        tax = (self.calculate_monthly_tax(monthly_base) / Decimal('2')).quantize(Decimal('0.01'))
        post_tax_deductions = Decimal('250')

        net_salary = (final_gross - pre_tax_deductions - tax - post_tax_deductions).quantize(Decimal('0.01'))

        return Payroll.objects.create(
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

    def calculate_monthly_tax(self, gross: Decimal) -> Decimal:
        if gross <= 20000:
            return gross * Decimal('0.05')
        elif gross <= 40000:
            return gross * Decimal('0.10')
        else:
            return gross * Decimal('0.15')
            
class PayrollSummarySerializer(serializers.Serializer):
    """Payroll Summary Report"""
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    total_employees = serializers.IntegerField()
    total_gross_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_overtime_pay = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_holiday_pay = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_deductions = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_net_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_net_salary = serializers.DecimalField(max_digits=12, decimal_places=2)