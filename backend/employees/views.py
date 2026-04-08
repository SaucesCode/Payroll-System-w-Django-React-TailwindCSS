# employees/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Employee
from .serializers import EmployeeSerializer
from users.permissions import IsPayrollOfficer, IsOwnerOrPayrollOfficer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Anyone authenticated can view, but employees see only their own
            return [IsAuthenticated(), IsOwnerOrPayrollOfficer()]
        else:
            # Create, update, delete → only Payroll Officer or Admin
            return [IsAuthenticated(), IsPayrollOfficer()]