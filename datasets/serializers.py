from rest_framework import serializers
from datasets.models import datasets

class datasetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = datasets
        fields = '__all__'
