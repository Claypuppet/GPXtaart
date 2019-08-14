from django.urls import path
from django.contrib.auth import views as auth_views

from smart_energy.views import ApiMeterList, ApiMeterDetail, ApiPowerMeasurementList, ApiGasMeasurementList, \
    DashboardPage, DashboardGasPage, DashboardPowerPage

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='login.html')),
    path('logout/', auth_views.logout_then_login, name='logout'),
    path('dashboard/', DashboardPage.as_view(), name='dashboard'),
    path('dashboard/power', DashboardPowerPage.as_view(), name='dashboard_power'),
    path('dashboard/gas', DashboardGasPage.as_view(), name='dashboard_gas'),
    path('api/meters/', ApiMeterList.as_view()),
    path('api/meters/<int:pk>/', ApiMeterDetail.as_view()),
    path('api/meters/<int:meter_id>/energy/', ApiPowerMeasurementList.as_view()),
    path('api/meters/<int:meter_id>/gas/', ApiGasMeasurementList.as_view()),
]
