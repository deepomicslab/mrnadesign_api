from rest_framework import serializers
from tsnadb.models import tsnadb_validated, tsnadb_neoantigen


class tsnadb2ValidatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = tsnadb_validated
        fields = '__all__'

class tsnadb2NeoantigenSerializer(serializers.ModelSerializer):
    class Meta:
        model = tsnadb_neoantigen
        fields = '__all__'