from rest_framework import serializers
from isoform_samples.models import Samples


class SamplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Samples
        fields = '__all__'
