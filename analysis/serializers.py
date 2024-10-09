from rest_framework import serializers
from analysis.models import analysis


class analysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = analysis
        fields = '__all__'
