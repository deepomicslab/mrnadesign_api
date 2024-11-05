from rest_framework import serializers
from taskresult.models import (
    lineardesign_taskresult,
    prediction_taskresult,
)


class lineardesign_taskresultSerializer(serializers.ModelSerializer):
    class Meta:
        model = lineardesign_taskresult
        fields = '__all__'

class prediction_taskresultSerializer(serializers.ModelSerializer):
    class Meta:
        model = prediction_taskresult
        fields = '__all__'