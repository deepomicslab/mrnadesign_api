from rest_framework import serializers
from codon.models import CodonPair

class CodonPairSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodonPair
        fields = '__all__'