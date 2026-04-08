# attendance/serializers.py
from rest_framework import serializers
from datetime import date, timedelta
from .models import Attendance, Holiday
from employees.serializers import EmployeeSerializer
from employees.models import Employee
class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )

    total_days = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            'id',
            'employee',
            'employee_id',
            'days_worked',
            'absences',
            'overtime_hours',
            'holiday_worked',          # ← New
            'period_start',
            'period_end',
            'total_days',
        ]
        read_only_fields = ['id', 'days_worked', 'total_days']

    def get_total_days(self, obj):
        return obj.days_worked + obj.absences