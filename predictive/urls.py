"""
URL configuration for AIMaintenance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from predictive import views as pred
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('predictive_screen/', pred.predictive_screen, name='predictive_screen'),
    path('run_predictions/', pred.run_predictions, name='ajax_predictive_screen-data'),
    path('training_screen/', pred.training_screen, name='training_screen'),
    path('model_analysis/', pred.model_analysis, name='model_analysis'),
    path('get_models/', pred.get_models, name='get_models'),
    path('model_analysis_chart/', pred.model_evaluation, name='model_evaluation'),
    path('check_server/', pred.is_server_live),
    path('datalog/', pred.datalog),
    path('pred_sensors/', pred.get_pred_sensor_list),
    path('sensordata/', pred.get_sensor_data),
    path('datalog_sensor/', pred.datalog_sensor_list),
    path('error_log/', pred.error_log),
    path('test/', pred.test_function),
    path('train_model/', pred.train_model, name='train_model'),
    path('data/', pred.element_raw_data, name='ajax_sensor-data'),
    path('predict/', pred.run_predictions),
    path('delete_all/<str:sensor_id>', pred.delete_all_records),
    path('anamoly_records/', pred.refresh_anomalies),
    path('alert/', pred.email_anamoly_alert),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
