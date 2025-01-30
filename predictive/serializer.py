from rest_framework import serializers
from .models import *


class SensorDataLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorDataLog
        exclude = ['id']


class ErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorLog
        exclude = ['id']


class SettingsElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingsElement
        fields = '__all_'
