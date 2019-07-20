from django.urls import path
from django.contrib.auth import views as auth_views

from smart_energy.views import ApiMeterList, ApiMeterDetail, ApiPowerMeasurementList, ApiGasMeasurementList, DashboardPage

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='login.html')),
    path('logout/', auth_views.logout_then_login),
    path('dashboard/', DashboardPage.as_view()),
    path('api/meters/', ApiMeterList.as_view()),
    path('api/meters/<int:pk>/', ApiMeterDetail.as_view()),
    path('api/meters/<int:meter_id>/energy/', ApiPowerMeasurementList.as_view()),
    path('api/meters/<int:meter_id>/gas/', ApiGasMeasurementList.as_view()),
]
