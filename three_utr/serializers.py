from rest_framework import serializers
from three_utr.models import three_utr


class three_utrSerializer(serializers.ModelSerializer):
    class Meta:
        model = three_utr
        fields = '__all__'