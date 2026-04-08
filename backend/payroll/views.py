# payroll/views.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .models import Payroll
from .serializers import PayrollSerializer
from users.permissions import IsPayrollOfficer, IsOwnerOrPayrollOfficer

class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['period_start', 'period_end']
    ordering_fields = ['period_start', 'period_end', 'employee__last_name']
    ordering = ['-period_start', '-period_end']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), IsOwnerOrPayrollOfficer()]
        return [IsAuthenticated(), IsPayrollOfficer()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_payroll_officer:
            return queryset
        # Regular employees can only see their own payroll
        if hasattr(user, 'employee_profile') and user.employee_profile:
            return queryset.filter(employee=user.employee_profile)
        return queryset.none()