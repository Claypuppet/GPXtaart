from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Meter)
admin.site.register(PowerMeasurement)
admin.site.register(GasMeasurement)
