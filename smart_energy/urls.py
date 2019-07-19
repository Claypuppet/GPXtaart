
from django.urls import path

from smart_energy.views import ApiMeterList

urlpatterns = [
    path('', ApiMeterList.as_view()),
    path('api/meters/', ApiMeterList.as_view()),
    path('api/meters/<int:id>/', ApiMeterList.as_view()),
    path('api/meters/<int:id>/energy/', ApiMeterList.as_view()),
    path('api/meters/<int:id>/gas/', ApiMeterList.as_view()),
]
