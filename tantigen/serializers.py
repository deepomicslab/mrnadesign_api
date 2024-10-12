from rest_framework import serializers
from tantigen.models import tantigen


class tantigenSerializer(serializers.ModelSerializer):
    class Meta:
        model = tantigen
        fields = '__all__'