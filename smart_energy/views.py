from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from smart_energy.models import Meter, PowerMeasurement, GasMeasurement
from smart_energy.serializers import MeterListSerializer, GasMeasurementListSerializer, \
    PowerMeasurementListSerializer, MeterDetailSerializer


class DashboardPage(LoginRequiredMixin, View):
    template_name = 'dashboard.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'meters': Meter.objects.all()
        })


class DashboardPowerPage(DashboardPage):
    template_name = 'dashboard_power.html'


class DashboardGasPage(DashboardPage):
    template_name = 'dashboard_gas.html'


class ApiMeterList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MeterListSerializer
    queryset = Meter.objects.all()


class ApiMeterDetail(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MeterDetailSerializer
    queryset = Meter.objects.all()


class ApiPowerMeasurementList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PowerMeasurementListSerializer

    def get_queryset(self):
        return PowerMeasurement.objects.filter(meter_id=self.kwargs.get('meter_id'))


class ApiGasMeasurementList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GasMeasurementListSerializer

    def get_queryset(self):
        return GasMeasurement.objects.filter(meter_id=self.kwargs.get('meter_id'))
