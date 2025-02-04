from rest_framework import serializers
from taskresult.models import (
    prediction_taskresult,
)

class prediction_taskresultSerializer(serializers.ModelSerializer):
    class Meta:
        model = prediction_taskresult
        fields = '__all__'