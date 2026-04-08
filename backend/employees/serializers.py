# employees/serializers.py
from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'employee_id',
            'first_name',
            'last_name',
            'middle_name',
            'full_name',
            'date_of_birth',
            'gender',
            'email',
            'phone_number',
            'address',
            'position',
            'department',
            'date_joined',
            'employment_status',
            'base_salary',
            'bank_name',
            'bank_account_number',
            'is_active',
        ]
        read_only_fields = ['id', 'full_name']

    def get_full_name(self, obj):
        middle = f" {obj.middle_name}" if obj.middle_name else ""
        return f"{obj.first_name}{middle} {obj.last_name}".strip()

    def validate_employee_id(self, value):
        """Optional: Add custom validation for employee_id format"""
        if value and not value.startswith('EMP-'):
            raise serializers.ValidationError("Employee ID should start with 'EMP-' (e.g., EMP-001)")
        return value