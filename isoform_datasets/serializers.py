from rest_framework import serializers
from isoform_datasets.models import Datasets


class DatasetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Datasets
        fields = '__all__'
