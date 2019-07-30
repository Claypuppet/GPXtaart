import datetime
import re
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from smart_energy.managers import PowerMeasurementManager, GasMeasurementManager, MeterManager


class Measurement(models.Model):
    class Meta:
        abstract = True

    moment = models.DateTimeField(editable=False)  # 0-1:24.2.1(101209110000W)
    consumption = models.DecimalField(max_digits=9, decimal_places=3, editable=False)  # 0-1:24.2.1(12785.123*m3)

    avg_min_consumption = models.DecimalField(max_digits=9, decimal_places=3, editable=False, null=True)
    avg_hour_consumption = models.DecimalField(max_digits=9, decimal_places=3, editable=False, null=True)

    def __str__(self):
        return "Measurement %s" % self.moment.strftime("%Y-%m-%d %H:%M:%S")


class PowerMeasurement(Measurement):
    objects = PowerMeasurementManager()

    meter = models.ForeignKey('Meter', models.CASCADE, related_name='power_measurements')

    tariff = models.SmallIntegerField(editable=False)  # 0-0:96.14.0(0002)
    production = models.DecimalField(max_digits=9, decimal_places=3, editable=False)  # 1-0:2.7.0(00.000*kW)

    avg_min_production = models.DecimalField(max_digits=9, decimal_places=3, editable=False, null=True)
    avg_hour_production = models.DecimalField(max_digits=9, decimal_places=3, editable=False, null=True)


class GasMeasurement(Measurement):
    objects = GasMeasurementManager()

    meter = models.ForeignKey('Meter', models.CASCADE, related_name='gas_measurements')


class Meter(models.Model):
    objects = MeterManager()

    last_raw = models.TextField()
    version = models.IntegerField()  # 1-3:0.2.8(40)
    sn_pow = models.CharField(max_length=255)  # 0-0:96.1.1(sn_dddddddd)
    sn_gas = models.CharField(max_length=255)  # 0-1:96.1.0(sn_ddddd)
    cons_1 = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:1.8.1(123456.789*kWh)
    cons_2 = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:1.8.2(123456.789*kWh)
    prod_1 = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:2.8.1(123456.789*kWh)
    prod_2 = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:2.8.2(123456.789*kWh)
    tariff = models.SmallIntegerField(default=1)  # 0-0:96.14.0(0002)
    gas = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:2.8.2(123456.789*kWh)

    pow_fail = models.IntegerField(default=-1)  # 0-0:96.7.21(00004)
    long_pow_fail = models.IntegerField(default=-1)  # 0-0:96.7.9(00002)
    vol_sag_1 = models.IntegerField(default=-1)  # 1-0:32.32.0(00002)
    vol_sag_2 = models.IntegerField(default=-1)  # 1-0:52.32.0(00001)
    vol_sag_3 = models.IntegerField(default=-1)  # 1-0:72:32.0(00000)
    vol_swell_1 = models.IntegerField(default=-1)  # 1-0:32.36.0(00000)
    vol_swell_2 = models.IntegerField(default=-1)  # 1-0:52.36.0(00003)
    vol_swell_3 = models.IntegerField(default=-1)  # 1-0:72.36.0(00000)

    @property
    def last_power_measurement(self) -> PowerMeasurement:
        return self.power_measurements.last()

    @property
    def last_gas_measurement(self) -> GasMeasurement:
        return self.gas_measurements.last()

    def __str__(self):
        return "Meter %s" % self.sn_pow


class ReadingContainer(models.Model):
    class Meta:
        # No database model needed
        abstract = True

    _df = r"\((?P<year>\d{2})(?P<month>\d{2})(?P<day>\d{2})(?P<hour>\d{2})(?P<min>\d{2})(?P<sec>\d{2})(?P<ws>W|S)\)"

    completed = False

    last_raw = models.TextField()
    version = models.IntegerField()  # 1-3:0.2.8(40)
    sn_pow = models.CharField(max_length=255)  # 0-0:96.1.1(sn_dddddddd)
    sn_gas = models.CharField(max_length=255)  # 0-1:96.1.0(sn_ddddd)
    cons_1 = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:1.8.1(123456.789*kWh)
    cons_2 = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:1.8.2(123456.789*kWh)
    prod_1 = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:2.8.1(123456.789*kWh)
    prod_2 = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:2.8.2(123456.789*kWh)
    tariff = models.SmallIntegerField()  # 0-0:96.14.0(0002)
    gas = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:2.8.2(123456.789*kWh)

    pow_fail = models.IntegerField()  # 0-0:96.7.21(00004)
    long_pow_fail = models.IntegerField()  # 0-0:96.7.9(00002)
    vol_sag_1 = models.IntegerField(default=-1)  # 1-0:32.32.0(00002)
    vol_sag_2 = models.IntegerField(default=-1)  # 1-0:52.32.0(00001)
    vol_sag_3 = models.IntegerField(default=-1)  # 1-0:72:32.0(00000)
    vol_swell_1 = models.IntegerField(default=-1)  # 1-0:32.36.0(00000)
    vol_swell_2 = models.IntegerField(default=-1)  # 1-0:52.36.0(00003)
    vol_swell_3 = models.IntegerField(default=-1)  # 1-0:72.36.0(00000)

    # Power measurement
    power_moment = models.DateTimeField()  # 0-0:1.0.0(101209113020W)

    @property
    def power_tariff(self):
        return self.tariff

    power_consumption = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:1.7.0(01.1 93*kW)
    power_production = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:2.7.0(00.000*kW)

    # Gas measurement
    gas_moment = models.DateTimeField()  # 0-1:24.2.1(101209110000W)

    @property
    def gas_consumption(self):
        return 0

    def save(self, **kwargs):
        try:
            self.clean_fields()
            meter, created = Meter.objects.update_or_create(
                {
                    'version': self.version,
                    'sn_pow': self.sn_pow,
                    'sn_gas': self.sn_gas,
                    'cons_1': self.cons_1,
                    'cons_2': self.cons_2,
                    'prod_1': self.prod_1,
                    'prod_2': self.prod_2,
                    'gas': self.gas,
                    'tariff': self.power_tariff,
                    'pow_fail': self.pow_fail,
                    'long_pow_fail': self.long_pow_fail,
                    'vol_sag_1': self.vol_sag_1,
                    'vol_sag_2': self.vol_sag_2,
                    'vol_sag_3': self.vol_sag_3,
                    'vol_swell_1': self.vol_swell_1,
                    'vol_swell_2': self.vol_swell_2,
                    'vol_swell_3': self.vol_swell_3,
                    'last_raw': self.last_raw
                },
                sn_pow=self.sn_pow,
                sn_gas=self.sn_gas,
            )

            meter.power_measurements.create(
                moment=self.power_moment,
                tariff=self.power_tariff,
                consumption=self.power_consumption,
                production=self.power_production,
            )
            meter.gas_measurements.create(
                moment=self.gas_moment,
                consumption=self.gas_consumption,
            )
        except ValidationError as e:
            print('not saved', e)
            for field, errors in e.error_dict.items():
                print(field, errors, getattr(self, field))

    def parse_line(self, line: str):
        self.last_raw += line

        if line.startswith('1-3:0.2.8'):
            self.version = int(re.search(r"\((\d+)\)", line)[1])
        elif line.startswith('0-0:1.0.0'):
            moment = re.search(self._df, line)
            self.power_moment = datetime.datetime(
                year=2000 + int(moment.group("year")),
                month=int(moment.group("month")),
                day=int(moment.group("day")),
                hour=int(moment.group("hour")) - (1 if moment.group("ws") == "S" else 0),
                minute=int(moment.group("min")),
                second=int(moment.group("sec")),
            ).astimezone(datetime.timezone.utc)
        elif line.startswith('0-0:96.1.1'):
            self.sn_pow = re.search(r"\((.*)\)", line)[1]
        elif line.startswith('1-0:1.8.1'):
            self.cons_1 = Decimal(re.search(r"\((\d+\.\d+)\*kWh\)", line)[1])
        elif line.startswith('1-0:1.8.2'):
            self.cons_2 = Decimal(re.search(r"\((\d+\.\d+)\*kWh\)", line)[1])
        elif line.startswith('1-0:2.8.1'):
            self.prod_1 = Decimal(re.search(r"\((\d+\.\d+)\*kWh\)", line)[1])
        elif line.startswith('1-0:2.8.2'):
            self.prod_2 = Decimal(re.search(r"\((\d+\.\d+)\*kWh\)", line)[1])
        elif line.startswith('0-0:96.14.0'):
            self.tariff = int(re.search(r"\((\d+)\)", line)[1])
        elif line.startswith('1-0:1.7.0'):
            self.power_consumption = Decimal(re.search(r"\((\d+\.\d+)\*kW\)", line)[1])
        elif line.startswith('1-0:2.7.0'):
            self.power_production = Decimal(re.search(r"\((\d+\.\d+)\*kW\)", line)[1])
        elif line.startswith('0-0:96.7.21'):
            self.pow_fail = int(re.search(r"\((\d+)\)", line)[1])
        elif line.startswith('0-0:96.7.9'):
            self.long_pow_fail = int(re.search(r"\((\d+)\)", line)[1])
        elif line.startswith('1-0:99:97.0'):
            # TODO: parse fail logs
            pass
        elif line.startswith('1-0:32.32.0'):
            self.vol_sag_1 = int(re.search(r"\((\d+)\)", line)[1])
        elif line.startswith('1-0:52.32.0'):
            self.vol_sag_2 = int(re.search(r"\((\d+)\)", line)[1])
        elif line.startswith('1-0:72:32.0'):
            self.vol_sag_3 = int(re.search(r"\((\d+)\)", line)[1])
        elif line.startswith('1-0:32.36.0'):
            self.vol_swell_1 = int(re.search(r"\((\d+)\)", line)[1])
        elif line.startswith('1-0:52.36.0'):
            self.vol_swell_2 = int(re.search(r"\((\d+)\)", line)[1])
        elif line.startswith('1-0:72.36.0'):
            self.vol_swell_3 = int(re.search(r"\((\d+)\)", line)[1])
        elif line.startswith('0-1:96.1.0'):
            self.sn_gas = re.search(r"\(([^)]+)\)", line)[1]
        elif line.startswith('0-1:24.2.1'):
            moment = re.search(self._df, line)
            self.gas_moment = datetime.datetime(
                year=2000 + int(moment.group("year")),
                month=int(moment.group("month")),
                day=int(moment.group("day")),
                hour=int(moment.group("hour")) + (1 if moment.group("ws") == "S" else 0),
                minute=int(moment.group("min")),
                second=int(moment.group("sec")),
            ).astimezone(datetime.timezone.utc)
            self.gas = Decimal(re.search(r"\((\d+\.\d+)\*m3\)", line)[1])
        elif line.startswith('!'):
            self.completed = True
