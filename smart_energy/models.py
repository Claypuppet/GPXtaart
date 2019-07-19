import datetime
import re

from django.db import models


class Meter(models.Model):
    version = models.IntegerField()  # 1-3:0.2.8(40)
    sn_pow = models.CharField(max_length=255)  # 0-0:96.1.1(sn_dddddddd)
    sn_gas = models.CharField(max_length=255)  # 0-1:96.1.0(sn_ddddd)
    cons_1 = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:1.8.1(123456.789*kWh)
    cons_2 = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:1.8.2(123456.789*kWh)
    prod_1 = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:2.8.1(123456.789*kWh)
    prod_2 = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:2.8.2(123456.789*kWh)
    gas = models.DecimalField(max_digits=9, decimal_places=3)  # 1-0:2.8.2(123456.789*kWh)

    pow_fail = models.IntegerField(default=-1)  # 0-0:96.7.21(00004)
    long_pow_fail = models.IntegerField(default=-1)  # 0-0:96.7.9(00002)
    vol_sag_1 = models.IntegerField(default=-1)  # 1-0:32.32.0(00002)
    vol_sag_2 = models.IntegerField(default=-1)  # 1-0:52.32.0(00001)
    vol_sag_3 = models.IntegerField(default=-1)  # 1-0:72:32.0(00000)
    vol_swell_1 = models.IntegerField(default=-1)  # 1-0:32.36.0(00000)
    vol_swell_2 = models.IntegerField(default=-1)  # 1-0:52.36.0(00003)
    vol_swell_3 = models.IntegerField(default=-1)  # 1-0:72.36.0(00000)

    last_raw = models.TextField()

    def __str__(self):
        return "Meter %s" % self.sn_pow


class PowerMeasurement(models.Model):
    meter = models.ForeignKey(Meter, models.CASCADE, 'power_measurements')

    moment = models.DateTimeField(editable=False)  # 0-0:1.0.0(101209113020W)
    tariff = models.SmallIntegerField(editable=False)  # 0-0:96.14.0(0002)
    consumption = models.DecimalField(max_digits=9, decimal_places=3, editable=False)  # 1-0:1.7.0(01.1 93*kW)
    production = models.DecimalField(max_digits=9, decimal_places=3, editable=False)  # 1-0:2.7.0(00.000*kW)


class GasMeasurement(models.Model):
    meter = models.ForeignKey(Meter, models.CASCADE, 'gas_measurements')

    moment = models.DateTimeField(editable=False)  # 0-1:24.2.1(101209110000W)
    consumption = models.DecimalField(max_digits=9, decimal_places=3, editable=False)  # 0-1:24.2.1(12785.123*m3)


class ReadingContainer(object):
    _df = r"\((?P<year>\d{2})(?P<month>\d{2})(?P<day>\d{2})(?P<hour>\d{2})(?P<min>\d{2})(?P<sec>\d{2})(?P<ws>W|S)\)"

    def __init__(self):
        self.raw_lines = None
        self.version = None
        self.sn_pow = None
        self.sn_gas = None
        self.cons_1 = None
        self.cons_2 = None
        self.prod_1 = None
        self.prod_2 = None
        self.gas = None
        self.pow_fail = None
        self.long_pow_fail = None
        self.vol_sag_1 = None
        self.vol_sag_2 = None
        self.vol_sag_3 = None
        self.vol_swell_1 = None
        self.vol_swell_2 = None
        self.vol_swell_3 = None
        self.power_moment = None
        self.power_tariff = None
        self.power_consumption = None
        self.power_production = None
        self.gas_moment = None

        self._reset()

    def _reset(self):
        self.raw_lines = ''
        self.version = -1
        self.sn_pow = ''
        self.sn_gas = ''
        self.cons_1 = 0
        self.cons_2 = 0
        self.prod_1 = 0
        self.prod_2 = 0
        self.gas = 0
        self.pow_fail = -1
        self.long_pow_fail = -1
        self.vol_sag_1 = -1
        self.vol_sag_2 = -1
        self.vol_sag_3 = -1
        self.vol_swell_1 = -1
        self.vol_swell_2 = -1
        self.vol_swell_3 = -1
        self.power_moment = None
        self.power_tariff = -1
        self.power_consumption = -1
        self.power_production = -1
        self.gas_moment = None

    def _is_valid(self):
        return True

    def _meter_data(self):
        return {
            'version': self.version,
            'sn_pow': self.sn_pow,
            'sn_gas': self.sn_gas,
            'cons_1': self.cons_1,
            'cons_2': self.cons_2,
            'prod_1': self.prod_1,
            'prod_2': self.prod_2,
            'gas': self.gas,
            'pow_fail': self.pow_fail,
            'long_pow_fail': self.long_pow_fail,
            'vol_sag_1': self.vol_sag_1,
            'vol_sag_2': self.vol_sag_2,
            'vol_sag_3': self.vol_sag_3,
            'vol_swell_1': self.vol_swell_1,
            'vol_swell_2': self.vol_swell_2,
            'vol_swell_3': self.vol_swell_3,
            'last_raw': self.raw_lines
        }

    def _save(self):
        if self._is_valid():
            meter, created = Meter.objects.update_or_create(
                self._meter_data(),
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
                consumption=0,  # self.gas calculation
            )
            print('saved new reading')
        self._reset()

    def parse_line(self, line: str):
        self.raw_lines += line

        if line.startswith('1-3:0.2.8'):
            self.version = int(re.search(r"\((\d+)\)", line)[1])
        elif line.startswith('0-0:1.0.0'):
            moment = re.search(self._df, line)
            self.power_moment = datetime.datetime(
                year=2000 + int(moment.group("year")),
                month=int(moment.group("month")),
                day=int(moment.group("day")),
                hour=int(moment.group("hour")) + (1 if moment.group("ws") == "S" else 0),
                minute=int(moment.group("min")),
                second=int(moment.group("sec")),
            ).astimezone(datetime.timezone.utc)
        elif line.startswith('0-0:96.1.1'):
            self.sn_pow = re.search(r"\((.*)\)", line)[1]
        elif line.startswith('1-0:1.8.1'):
            self.cons_1 = float(re.search(r"\((\d+\.\d+)\*kWh\)", line)[1])
        elif line.startswith('1-0:1.8.2'):
            self.cons_2 = float(re.search(r"\((\d+\.\d+)\*kWh\)", line)[1])
        elif line.startswith('1-0:2.8.1'):
            self.prod_1 = float(re.search(r"\((\d+\.\d+)\*kWh\)", line)[1])
        elif line.startswith('1-0:2.8.2'):
            self.prod_2 = float(re.search(r"\((\d+\.\d+)\*kWh\)", line)[1])
        elif line.startswith('0-0:96.14.0'):
            self.power_tariff = int(re.search(r"\((\d+)\)", line)[1])
        elif line.startswith('1-0:1.7.0'):
            self.power_consumption = float(re.search(r"\((\d+\.\d+)\*kW\)", line)[1])
        elif line.startswith('1-0:2.7.0'):
            self.power_production = float(re.search(r"\((\d+\.\d+)\*kW\)", line)[1])
        elif line.startswith('0-0:96.7.21'):
            self.pow_fail = int(re.search(r"\((\d+)\)", line)[1])
        elif line.startswith('0-0:96.7.9'):
            self.long_pow_fail = int(re.search(r"\((\d+)\)", line)[1])
        elif line.startswith('1-0:99:97.0'):
            # fail logs
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
            self.gas = float(re.search(r"\((\d+\.\d+)\*m3\)", line)[1])
        elif line.startswith('!'):
            self._save()

        pass
