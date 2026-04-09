# payroll/views.py
from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg
from datetime import timedelta, date
from decimal import Decimal
from .models import Payroll
from .serializers import PayrollSerializer, PayrollSummarySerializer
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
        if hasattr(user, 'employee_profile') and user.employee_profile:
            return queryset.filter(employee=user.employee_profile)
        return queryset.none()


class PayrollSummaryView(APIView):
    """Payroll Summary Report for a specific period"""
    permission_classes = [IsAuthenticated, IsPayrollOfficer]
    serializer_class = PayrollSummarySerializer

    def get(self, request):
        period_start_str = request.query_params.get('period_start')
        period_end_str = request.query_params.get('period_end')

        # Auto-detect current bi-weekly period
        if not period_start_str or not period_end_str:
            today = date.today()
            if today.day <= 15:
                period_start = today.replace(day=1)
                period_end = today.replace(day=15)
            else:
                period_start = today.replace(day=16)
                next_month = today.replace(day=28) + timedelta(days=4)
                last_day = next_month.replace(day=1) - timedelta(days=1)
                period_end = last_day
        else:
            try:
                period_start = date.fromisoformat(period_start_str)
                period_end = date.fromisoformat(period_end_str)
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, 
                              status=status.HTTP_400_BAD_REQUEST)

        payrolls = Payroll.objects.filter(
            period_start=period_start,
            period_end=period_end
        )
  
        if not payrolls.exists():
            summary_data = {
                'period_start': period_start,
                'period_end': period_end,
                'total_employees': 0,
                'total_gross_salary': Decimal('0.00'),
                'total_overtime_pay': Decimal('0.00'),
                'total_holiday_pay': Decimal('0.00'),
                'total_deductions': Decimal('0.00'),
                'total_net_salary': Decimal('0.00'),
                'average_net_salary': Decimal('0.00'),
            }
            serializer = self.serializer_class(summary_data)
            return Response(serializer.data)

        # If payrolls exist, calculate real summary
        summary = payrolls.aggregate(
            total_employees=Count('employee'),
            total_gross=Sum('gross_salary'),
            total_overtime=Sum('overtime_pay'),
            total_holiday=Sum('holiday_pay'),
            total_pre_tax=Sum('pre_tax_deductions'),
            total_tax=Sum('tax'),
            total_post_tax=Sum('post_tax_deductions'),
            total_net=Sum('net_salary'),
            avg_net=Avg('net_salary')
        )

        total_deductions = (
            (summary['total_pre_tax'] or 0) +
            (summary['total_tax'] or 0) +
            (summary['total_post_tax'] or 0)
        )

        summary_data = {
            'period_start': period_start,
            'period_end': period_end,
            'total_employees': summary['total_employees'] or 0,
            'total_gross_salary': summary['total_gross'] or Decimal('0.00'),
            'total_overtime_pay': summary['total_overtime'] or Decimal('0.00'),
            'total_holiday_pay': summary['total_holiday'] or Decimal('0.00'),
            'total_deductions': total_deductions,
            'total_net_salary': summary['total_net'] or Decimal('0.00'),
            'average_net_salary': summary['avg_net'] or Decimal('0.00'),
        }

        serializer = self.serializer_class(summary_data)
        return Response(serializer.data)