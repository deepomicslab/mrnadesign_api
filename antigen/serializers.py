from rest_framework import serializers
from antigen.models import antigen


class antigenSerializer(serializers.ModelSerializer):
    class Meta:
        model = antigen
        fields = '__all__'