from rest_framework import serializers

from .models import Meter, PowerMeasurement, GasMeasurement


class PowerMeasurementListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PowerMeasurement
        fields = (
            'id',
            'moment',
            'tariff',
            'consumption',
            'production',
        )


class GasMeasurementListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GasMeasurement
        fields = (
            'id',
            'moment',
            'consumption',
        )


class MeterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter
        fields = (
            'id',
            'version',
            'sn_pow',
            'sn_gas',
            'cons_1',
            'cons_2',
            'prod_1',
            'prod_2',
            'tariff',
            'gas',
        )


class MeterDetailSerializer(serializers.ModelSerializer):
    last_power_measurement = PowerMeasurementListSerializer()
    last_gas_measurement = GasMeasurementListSerializer()

    class Meta:
        model = Meter
        fields = MeterListSerializer.Meta.fields + (
            'pow_fail',
            'long_pow_fail',
            'vol_sag_1',
            'vol_sag_2',
            'vol_sag_3',
            'vol_swell_1',
            'vol_swell_2',
            'vol_swell_3',
            'last_raw',
            'last_power_measurement',
            'last_gas_measurement',
        )
