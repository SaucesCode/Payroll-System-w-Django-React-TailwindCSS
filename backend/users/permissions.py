# users/permissions.py
from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """Only Admin can perform this action"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsPayrollOfficer(permissions.BasePermission):
    """Admin + Payroll Officer"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_payroll_officer


class IsOwnerOrPayrollOfficer(permissions.BasePermission):
    """
    Employees can only view their own data.
    Payroll Officers / Admin can view everything.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.is_payroll_officer:
            return True

        # For Employee role - check if it's their own record
        if hasattr(obj, 'employee'):
            return obj.employee == request.user.employee_profile
        elif hasattr(obj, 'user_account'):   # if checking Employee model
            return obj == request.user.employee_profile

        return False
    
    def has_permission(self, request, view):
        """Basic permission check before object level"""
        return request.user.is_authenticated