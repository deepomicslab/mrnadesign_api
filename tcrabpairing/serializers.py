from rest_framework import serializers
from tcrabpairing.models import tcrabpairing

class tcrabpairingSerializer(serializers.ModelSerializer):
    class Meta:
        model = tcrabpairing
        fields = '__all__'
