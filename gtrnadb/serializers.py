from rest_framework import serializers
from gtrnadb.models import gtrnadb_genome, gtrnadb_data


class gtrnadbGenomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = gtrnadb_genome
        fields = '__all__'

class gtrnadbDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = gtrnadb_data
        fields = '__all__'