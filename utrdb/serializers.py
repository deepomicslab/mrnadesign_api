from rest_framework import serializers
from utrdb.models import utrdb


class utrdbSerializer(serializers.ModelSerializer):
    class Meta:
        model = utrdb
        fields = '__all__'