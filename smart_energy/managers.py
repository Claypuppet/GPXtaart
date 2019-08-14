import datetime

from django.db import models
from django.db.models import Avg


class MeasurementManager(models.Manager):
    def create(self, moment, **kwargs):
        """
        :type moment: datetime.datetime
        :type kwargs: dict
        :return:
        """
        meter = kwargs.get('meter', None) or self.instance
        """ :type: smart_energy.models.Meter"""
        avg_min_consumption = None
        avg_hour_consumption = None
        if meter.last_gas_measurement:
            last_moment = meter.last_gas_measurement.moment.astimezone(datetime.timezone.utc)
            if last_moment.minute is not moment.minute:
                start_moment = last_moment.replace(second=0)
                qs = meter.gas_measurements.filter(moment__gte=start_moment, moment__lt=moment)
                avg_min_consumption = list(qs.aggregate(Avg('consumption')).values())[0]
            if last_moment.hour is not moment.hour:
                start_moment = last_moment.replace(minute=0, second=0)
                qs = meter.gas_measurements.filter(moment__gte=start_moment, moment__lt=moment)
                avg_min_consumption = list(qs.aggregate(Avg('consumption')).values())[0]
        return super().create(
            avg_min_consumption=avg_min_consumption,
            avg_hour_consumption=avg_hour_consumption,
            moment=moment,
            **kwargs
        )


class PowerMeasurementManager(models.Manager):
    def create(self, moment, **kwargs):
        """
        :type moment: datetime.datetime
        :type kwargs: dict
        :return:
        """
        meter = kwargs.get('meter', None) or self.instance
        """ :type: smart_energy.models.Meter"""
        avg_min_production = None
        avg_hour_production = None
        if meter.last_power_measurement:
            last_moment = meter.last_power_measurement.moment.astimezone(datetime.timezone.utc)
            if last_moment.minute is not moment.minute:
                start_moment = last_moment.replace(second=0)
                qs = meter.power_measurements.filter(moment__gte=start_moment, moment__lt=moment)
                avg_min_production = list(qs.aggregate(Avg('production')).values())[0]
            if last_moment.hour is not moment.hour:
                start_moment = last_moment.replace(minute=0, second=0)
                qs = meter.power_measurements.filter(moment__gte=start_moment, moment__lt=moment)
                avg_min_production = list(qs.aggregate(Avg('production')).values())[0]
        return super().create(
            avg_min_consumption=avg_min_production,
            avg_hour_consumption=avg_hour_production,
            moment=moment,
            **kwargs
        )


class GasMeasurementManager(models.Manager):
    def create(self, **kwargs):
        return super().create(
            **kwargs
        )


class MeterManager(models.Manager):
    def get_or_create(self, defaults=None, **kwargs):
        return super().get_or_create(defaults, **kwargs)
