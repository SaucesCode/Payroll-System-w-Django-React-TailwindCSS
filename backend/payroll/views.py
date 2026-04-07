from rest_framework import viewsets
from .models import Payroll
from .serializers import PayrollSerializer
from rest_framework.permissions import IsAuthenticated

class PayrollViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer